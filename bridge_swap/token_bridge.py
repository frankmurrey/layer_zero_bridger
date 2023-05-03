import time

from bridge_swap.base_bridge import BridgeBase
from src.files_manager import read_evm_wallets_from_file
from src.schemas.config import ConfigSchema
from src.config import print_config

from loguru import logger


def token_mass_transfer(config_data: ConfigSchema):
    print_config(config=config_data,
                 log_text="Starting token bridge in 5 sec")

    wallets = read_evm_wallets_from_file()
    token_bridge = TokenBridgeManual(config=config_data)
    wallet_number = 1
    for wallet in wallets:
        token_bridge.transfer(private_key=wallet, wallet_number=wallet_number)
        wallet_number += 1


def token_mass_approve(config_data: ConfigSchema):
    print_config(config=config_data,
                 log_text="Starting token approve and check proccess in 5 sec")

    time.sleep(1)
    wallets = read_evm_wallets_from_file()
    token_bridge = TokenBridgeManual(config=config_data)
    wallet_number = 1
    time_start = time.time()
    for wallet in wallets:
        token_bridge.approve_token_transfer(private_key=wallet, wallet_number=wallet_number)
        wallet_number += 1
    time_end = time.time() - time_start

    if time_end < 30:
        logger.warning(f"Approve process took less than 30 sec. Waiting 20 sec to start bridge process")
        if config_data.test_mode is False:
            time.sleep(20)
        else:
            time.sleep(1)


class TokenBridgeManual(BridgeBase):
    def __init__(self, config: ConfigSchema):
        super().__init__(config=config)
        try:
            self.token_obj = self.bridge_manager.detect_coin(coin_query=config.coin_to_transfer,
                                                             chain_query=self.config_data.source_chain)
            self.token_contract = self.web3.eth.contract(address=self.token_obj.address,
                                                         abi=self.token_obj.abi)

        except AttributeError:
            logger.error(f"Bridge of {self.config_data.coin_to_transfer} is not supported between"
                         f" {self.config_data.source_chain} and {self.config_data.target_chain}")

    def approve_token_transfer(self, private_key, wallet_number):
        wallet_address = self.get_wallet_address(private_key=private_key)

        allowed_amount_to_bridge = self.check_allowance(wallet_address=wallet_address,
                                                        token_contract=self.token_contract,
                                                        spender=self.source_chain.router_address)

        if allowed_amount_to_bridge > self.max_bridge_amount:
            logger.info(f"[{wallet_number}] [{wallet_address}] - Has enough allowance for {self.token_obj.name} bridge")
            return

        approve_amount = int(1000000 * 10 ** self.get_token_decimals(self.token_contract))
        allowance_txn = self.build_allowance_tx(wallet_address=wallet_address,
                                                token_contract=self.token_contract,
                                                amount_out=approve_amount,
                                                spender=self.source_chain.router_address)
        try:
            estimated_gas_limit = self.get_estimate_gas(transaction=allowance_txn)

            if self.config_data.gas_limit > estimated_gas_limit:
                allowance_txn['gas'] = int(estimated_gas_limit + (estimated_gas_limit * 0.6))

            if self.config_data.test_mode is True:
                logger.info(f"[{wallet_address}] - Estimated gas limit for {self.token_obj.name}"
                            f" approve: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(allowance_txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"[{wallet_number}] [{wallet_address}] - Approve transaction sent: {tx_hash.hex()}")

        except Exception as e:
            logger.error(f"[{wallet_number}] [{wallet_address}] - Error while sending approval transaction: {e}")
            return False

    def transfer(self, private_key, wallet_number):
        if not self.token_obj:
            return

        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_token_balance_wei = self.get_token_balance(wallet_address=source_wallet_address,
                                                          token_contract=self.token_contract)
        wallet_token_balance = wallet_token_balance_wei / 10 ** self.get_token_decimals(self.token_contract)

        if self.config_data.send_to_one_address is True:
            dst_wallet_address = self.get_checksum_address(self.config_data.address_to_send)
        else:
            dst_wallet_address = wallet_address

        token_amount_out = self.get_random_amount_out(min_amount=self.min_bridge_amount,
                                                      max_amount=self.max_bridge_amount,
                                                      token_contract=self.token_contract)

        if wallet_token_balance_wei < token_amount_out:
            logger.error(f"[{wallet_number}] [{source_wallet_address}] - {self.config_data.coin_to_transfer} "
                         f"({self.config_data.source_chain})"
                         f" balance not enough "
                         f"to bridge. Balance: {wallet_token_balance}")
            return

        txn = self.build_token_bridge_tx(wallet_address=wallet_address,
                                         dst_wallet_address=dst_wallet_address,
                                         token_obj=self.token_obj,
                                         amount_out=token_amount_out,
                                         chain_id=self.target_chain.chain_id)

        try:
            estimated_gas_limit = self.get_estimate_gas(transaction=txn)

            if self.config_data.gas_limit > estimated_gas_limit:
                txn['gas'] = int(estimated_gas_limit + (estimated_gas_limit * 0.6))

            if self.config_data.test_mode is True:
                logger.info(f"[{wallet_number}] [{source_wallet_address}] - Estimated gas limit for "
                            f"{self.config_data.source_chain} → {self.config_data.target_chain} "
                            f"{self.token_obj.name} bridge: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"[{wallet_number}] [{source_wallet_address}] - Transaction sent: {tx_hash.hex()}")
        except Exception as e:
            logger.error(f"[{wallet_number}] [{source_wallet_address}] - Error while sending  transaction: {e}")
            return
