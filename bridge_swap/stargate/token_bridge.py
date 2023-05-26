import time
import random

from bridge_swap.base_bridge import BridgeBase
from src.files_manager import read_evm_wallets_from_file
from src.schemas.config import ConfigSchema
from src.config import print_config

from loguru import logger


def token_mass_transfer(config_data: ConfigSchema):
    print_config(config=config_data,
                 delay_seconds=10)

    wallets = read_evm_wallets_from_file()
    token_bridge = TokenBridgeManual(config=config_data)
    wallet_number = 1
    for wallet in wallets:
        token_bridge.transfer(private_key=wallet, wallet_number=wallet_number)
        wallet_number += 1
        time_delay = random.randint(config_data.min_delay_seconds, config_data.max_delay_seconds)
        if time_delay == 0:
            time.sleep(0.3)
            continue
        logger.info(f"Waiting {time_delay} seconds before next wallet bridge")
        time.sleep(time_delay)


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

    def get_allowance_amount_for_token(self, private_key):
        wallet_address = self.get_wallet_address(private_key=private_key,)
        return self.check_allowance(wallet_address=wallet_address,
                                    token_contract=self.token_contract,
                                    spender=self.source_chain.router_address)

    def allowance_check_loop(self, private_key, target_allowance_amount):
        while True:
            allowance_amount = self.get_allowance_amount_for_token(private_key=private_key)
            if allowance_amount >= target_allowance_amount:
                break
            time.sleep(2)

    def approve_token_transfer(self, allowance_txn, private_key, wallet_number, wallet_address):
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
            self.allowance_check_loop(private_key=private_key,
                                      target_allowance_amount=self.max_bridge_amount)
            logger.info(f"[{wallet_number}] [{wallet_address}] - Approve transaction confirmed")
            return True

        except Exception as e:
            logger.error(f"[{wallet_number}] [{wallet_address}] - Error while sending approval transaction: {e}")
            return False

    def transfer(self, private_key, wallet_number=None):
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

        if self.config_data.transfer_all_balance is True:
            token_amount_out = wallet_token_balance_wei
        else:
            token_amount_out = self.get_random_amount_out(min_amount=self.min_bridge_amount,
                                                          max_amount=self.max_bridge_amount,
                                                          token_contract=self.token_contract)
        if wallet_number is None:
            wallet_number = ""
        else:
            wallet_number = f"[{wallet_number}]"

        if wallet_token_balance_wei < token_amount_out:
            logger.error(f"{wallet_number} [{source_wallet_address}] - {self.config_data.coin_to_transfer} "
                         f"({self.config_data.source_chain})"
                         f" balance not enough "
                         f"to bridge. Balance: {wallet_token_balance}")
            return

        allowed_amount_to_bridge = self.check_allowance(wallet_address=wallet_address,
                                                        token_contract=self.token_contract,
                                                        spender=self.source_chain.router_address)

        if allowed_amount_to_bridge < token_amount_out:
            logger.warning(f"{wallet_number} [{source_wallet_address}] - Not enough allowance for {self.token_obj.name},"
                           f" approving {token_amount_out} {self.token_obj.name} to bridge")
            approve_amount = int(1000000 * 10 ** self.get_token_decimals(self.token_contract))
            allowance_txn = self.build_allowance_tx(wallet_address=wallet_address,
                                                    token_contract=self.token_contract,
                                                    amount_out=approve_amount,
                                                    spender=self.source_chain.router_address)
            approve_txn = self.approve_token_transfer(allowance_txn=allowance_txn,
                                                      private_key=private_key,
                                                      wallet_number=wallet_number,
                                                      wallet_address=wallet_address)
            if approve_txn is not True:
                return
        else:
            logger.info(f"{wallet_number} [{source_wallet_address}] - has enough allowance to bridge")

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
                logger.info(f"{wallet_number} [{source_wallet_address}] - Estimated gas limit for "
                            f"{self.config_data.source_chain} → {self.config_data.target_chain} "
                            f"{self.token_obj.name} bridge: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"{wallet_number} [{source_wallet_address}] - Transaction sent: {tx_hash.hex()}")

            return tx_hash.hex()
        except Exception as e:
            logger.error(f"{wallet_number} [{source_wallet_address}] - Error while sending  transaction: {e}")
            return
