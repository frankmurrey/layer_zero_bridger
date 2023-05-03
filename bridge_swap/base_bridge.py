import random

from src.schemas.config import ConfigSchema
from src.bridge_manager import BridgeManager

from eth_account import Account
from eth_abi import encode
from web3 import Web3


class BridgeBase:
    def __init__(self, config: ConfigSchema):
        self.bridge_manager = BridgeManager(input_data=config)
        self.config_data = config
        self.source_chain = self.bridge_manager.detect_chain(config.source_chain)
        self.target_chain = self.bridge_manager.detect_chain(config.target_chain)

        self.min_bridge_amount = config.min_bridge_amount
        self.max_bridge_amount = config.max_bridge_amount

        self.web3 = self.source_chain.web3

    def get_checksum_address(self, address):
        return self.web3.toChecksumAddress(address)

    def get_eth_balance(self, address):
        return self.web3.eth.get_balance(address)

    def get_token_balance(self, wallet_address, token_contract):
        balance = token_contract.functions.balanceOf(wallet_address).call()
        return balance

    def get_token_decimals(self, token_contract):
        decimals = token_contract.functions.decimals().call()
        return decimals

    def check_allowance(self, wallet_address, token_contract, spender):
        allowance = token_contract.functions.allowance(wallet_address, spender).call()
        return allowance

    def get_txn_fee(self, wallet_address) -> int:
        wallet_address = self.web3.to_checksum_address(wallet_address)
        fee = self.source_chain.router_contract.functions.quoteLayerZeroFee(self.target_chain.chain_id,
                                                                            1,
                                                                            wallet_address,
                                                                            "0x",
                                                                            [0, 0, wallet_address]
                                                                            ).call()
        return fee[0]

    def get_aptos_txn_fee(self, router_address, adapter_params, chain_id):
        fee = self.source_chain.endpoint_contract.functions.estimateFees(chain_id,
                                                                         router_address,
                                                                         "0x",
                                                                         False,
                                                                         adapter_params
                                                                         ).call()
        return fee[0]

    def get_estimate_gas(self, transaction):
        estimated_gas_limit = self.source_chain.web3.eth.estimate_gas(transaction)
        return estimated_gas_limit

    def get_wallet_nonce(self, wallet_address):
        return self.web3.eth.get_transaction_count(wallet_address)

    def get_wallet_address(self, private_key):
        account = Account.from_key(private_key)
        return self.web3.to_checksum_address(account.address)

    def get_amount_out_min(self, amount_out):
        return int(amount_out - (amount_out * self.config_data.slippage // 100))

    def get_gas_price(self):
        if self.config_data.custom_gas_price is True:
            if self.config_data.gas_price is not None:
                return self.web3.to_wei(self.config_data.gas_price, 'gwei')
            else:
                return self.web3.eth.gas_price
        else:
            return self.web3.eth.gas_price

    def get_src_pool_id(self, token_obj):
        return token_obj.pool_id

    def get_dst_pool_id(self, token_obj):
        src_token_name = token_obj.name
        token_objects = self.target_chain.token_contracts
        for token in token_objects:
            if token.name == src_token_name:
                return token.pool_id

        for token in token_objects:
            return token.pool_id

    def get_random_amount_out(self, min_amount, max_amount, token_contract=None):
        random_amount = random.uniform(min_amount, max_amount)

        if token_contract is None:
            token_amount_out = Web3.to_wei(random_amount, 'ether')
        else:
            token_amount_out = int(round(random_amount, 3) * 10 ** self.get_token_decimals(token_contract))

        return token_amount_out

    def gef_get_adapter_params(self, recipient_address: bytes):
        encoded_params = encode(["uint16", "uint256", "uint", "bytes32"],
                                [2, 10000, 0, recipient_address]).hex()
        params = '000' + encoded_params.lstrip('0')
        params_bytes = bytes.fromhex(params)
        return params_bytes

    def build_allowance_tx(self, wallet_address, token_contract, amount_out, spender):
        nonce = self.get_wallet_nonce(wallet_address=wallet_address)
        gas_price = self.get_gas_price()
        allowance_transaction = token_contract.functions.approve(
            spender,
            int(amount_out)
        ).build_transaction({
            'from': wallet_address,
            'gas': self.config_data.gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        return allowance_transaction

    def build_eth_bridge_tx(self, wallet_address, amount_out, chain_id, dst_wallet_address):
        fee: int = self.get_txn_fee(wallet_address=wallet_address)
        amount_out_min = self.get_amount_out_min(amount_out=amount_out)
        nonce = self.get_wallet_nonce(wallet_address=wallet_address)
        gas_price = self.get_gas_price()
        bridge_transaction = self.source_chain.eth_router_contract.functions.swapETH(
            chain_id,
            wallet_address,
            dst_wallet_address,
            amount_out,
            amount_out_min
        ).build_transaction({
            'from': wallet_address,
            'value': amount_out + fee,
            'gas': self.config_data.gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })

        return bridge_transaction

    def build_token_bridge_tx(self, wallet_address, amount_out, chain_id, token_obj, dst_wallet_address):
        fee: int = self.get_txn_fee(wallet_address=wallet_address)
        amount_out_min = self.get_amount_out_min(amount_out=amount_out)
        nonce = self.get_wallet_nonce(wallet_address=wallet_address)
        gas_price = self.get_gas_price()
        src_pool_id = self.get_src_pool_id(token_obj=token_obj)
        dst_pool_id = self.get_dst_pool_id(token_obj=token_obj)

        bridge_transaction = self.source_chain.router_contract.functions.swap(
            chain_id,
            src_pool_id,
            dst_pool_id,
            wallet_address,
            amount_out,
            amount_out_min,
            [0, 0, '0x0000000000000000000000000000000000000001'],
            dst_wallet_address,
            "0x"
        ).build_transaction({
            'from': wallet_address,
            'value': fee,
            'gas': self.config_data.gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })

        return bridge_transaction

    def build_token_bridge_to_aptos_tx(self, source_wallet_address, recipient_address: bytes, amount_out, token_obj):
        zro_payment_address = self.web3.to_checksum_address('0x0000000000000000000000000000000000000000')
        adapter_params = self.gef_get_adapter_params(recipient_address=recipient_address)
        fee: int = self.get_aptos_txn_fee(chain_id=108,
                                          router_address=self.source_chain.aptos_router_address,
                                          adapter_params=adapter_params)
        bridge_transaction = self.source_chain.aptos_router_contract.functions.sendToAptos(
            token_obj.address,
            recipient_address,
            amount_out,
            [source_wallet_address, zro_payment_address],
            adapter_params
        ).build_transaction({
            'from': source_wallet_address,
            'value': fee + (self.config_data.gas_limit * self.get_gas_price()),
            'gas': self.config_data.gas_limit,
            'gasPrice': self.get_gas_price(),
            'nonce': self.get_wallet_nonce(wallet_address=source_wallet_address),
        })

        return bridge_transaction

    def build_eth_bridge_to_aptos_tx(self, source_wallet_address, recipient_address: bytes, amount_out):
        zro_payment_address = self.web3.to_checksum_address('0x0000000000000000000000000000000000000000')
        adapter_params = self.gef_get_adapter_params(recipient_address=recipient_address)
        fee: int = self.get_aptos_txn_fee(chain_id=108,
                                          router_address=self.source_chain.aptos_router_address,
                                          adapter_params=adapter_params)
        bridge_transaction = self.source_chain.aptos_router_contract.functions.sendETHToAptos(
            recipient_address,
            amount_out,
            [source_wallet_address, zro_payment_address],
            adapter_params
        ).build_transaction({
            'from': source_wallet_address,
            'value': int(fee * 1.1 + amount_out),
            'gas': self.config_data.gas_limit,
            'gasPrice': self.get_gas_price(),
            'nonce': self.get_wallet_nonce(wallet_address=source_wallet_address),
        })

        return bridge_transaction
