import time
import random

from datetime import datetime, timedelta

from bridge_swap.base_bridge import BridgeBase
from src.files_manager import read_evm_wallets_from_file
from src.schemas.config import ConfigSchema
from src.config import print_config
from src.rpc_manager import RpcValidator

from loguru import logger


def core_mass_transfer(config_data: ConfigSchema):
    print_config(config=config_data)

    rpc_validator = RpcValidator()
    rpcs = rpc_validator.validated_rpcs

    wallets = read_evm_wallets_from_file()
    token_bridge = CoreDaoBridger(config=config_data)
    wallet_number = 1
    wallets_amount = len(wallets)
    for wallet in wallets:
        blured_wallet = token_bridge.blur_private_key(private_key=wallet)
        wallet_address = token_bridge.get_wallet_address(private_key=wallet)
        logger.info(f"[{wallet_number}] - {wallet_address}")
        logger.info(f"Got wallet pk /{blured_wallet}/")

        if config_data.source_chain.lower() == "bsc":
            bridge_status = token_bridge.transfer(private_key=wallet)
        else:
            bridge_status = token_bridge.transfer_from_core(private_key=wallet)

        if wallet_number == wallets_amount:
            logger.info(f"Bridge process is finished\n")
            break

        wallet_number += 1

        if bridge_status is not None:
            time_delay = random.randint(config_data.min_delay_seconds, config_data.max_delay_seconds)
        else:
            time_delay = 3

        if time_delay == 0:
            time.sleep(0.3)
            continue

        delta = timedelta(seconds=time_delay)
        result_datetime = datetime.now() + delta

        logger.info(f"Waiting {time_delay} seconds, next wallet bridge {result_datetime}\n")
        time.sleep(time_delay)


class CoreDaoBridger(BridgeBase):
    def __init__(self, config: ConfigSchema):
        super().__init__(config=config)
        try:
            self.token_obj = self.bridge_manager.detect_coin(coin_query=config.source_coin_to_transfer,
                                                             chain_query=self.config_data.source_chain)
            self.token_contract = self.web3.eth.contract(address=self.token_obj.address,
                                                         abi=self.token_obj.abi)

        except AttributeError:
            logger.error(f"Bridge of {self.config_data.source_coin_to_transfer} is not supported between"
                         f" {self.config_data.source_chain} and {self.config_data.target_chain}")

    def transfer(self, private_key, wallet_number=None):
        if not self.token_obj:
            return

        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_token_balance_wei = self.get_token_balance(wallet_address=source_wallet_address,
                                                          token_contract=self.token_contract)
        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** self.get_token_decimals(self.token_contract)

        if self.config_data.send_to_one_address is True:
            dst_wallet_address = self.get_checksum_address(self.config_data.address_to_send)
        else:
            dst_wallet_address = wallet_address

        if self.config_data.send_all_balance is True:
            token_amount_out_wei = wallet_token_balance_wei
            if token_amount_out_wei == 0:
                logger.error(f"{self.config_data.source_coin_to_transfer} "
                             f"({self.config_data.source_chain}) balance is 0")
                return
        else:
            token_amount_out_wei = self.get_random_amount_out(min_amount=self.min_bridge_amount,
                                                          max_amount=self.max_bridge_amount,
                                                          token_contract=self.token_contract)

        token_amount_out_decimals = token_amount_out_wei / 10 ** self.get_token_decimals(self.token_contract)

        if wallet_token_balance_wei < token_amount_out_wei:
            logger.error(f"{self.config_data.source_coin_to_transfer} ({self.config_data.source_chain})"
                         f" balance not enough to bridge. Balance: {wallet_token_balance_decimals}")
            return

        allowed_amount_to_bridge = self.check_allowance(wallet_address=wallet_address,
                                                        token_contract=self.token_contract,
                                                        spender=self.source_chain.core_dao_router_address)

        if allowed_amount_to_bridge < token_amount_out_wei:
            logger.warning(
                f"Not enough allowance for {self.token_obj.name}, approving {self.token_obj.name} to bridge")

            token_approval = self.make_approve_for_token(private_key=private_key,
                                                         target_approve_amount=token_amount_out_wei,
                                                         token_contract=self.token_contract,
                                                         token_obj=self.token_obj,
                                                         spender=self.source_chain.core_dao_router_address)

            if token_approval is not True:
                return
        else:
            logger.info(f"Wallet has enough allowance to bridge")

        txn = self.build_token_bridge_core_tx(wallet_address=wallet_address,
                                              amount_out=token_amount_out_wei,
                                              token_obj=self.token_obj,
                                              dst_wallet_address=dst_wallet_address)

        try:
            estimated_gas_limit = self.get_estimate_gas(transaction=txn)

            if self.config_data.gas_limit > estimated_gas_limit:
                txn['gas'] = estimated_gas_limit

            if self.config_data.test_mode is True:
                logger.success(
                    f"Estimated gas limit for {self.config_data.source_chain} → {self.config_data.target_chain}"
                    f" {self.token_obj.name} bridge: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            if self.config_data.wait_for_confirmation is True:
                time_out = self.config_data.confirmation_timeout_seconds
                tx_receipt = self.wait_for_tx_receipt(tx_hash=tx_hash, time_out=time_out)
                if tx_receipt['status'] == 1:
                    logger.success(
                        f"{self.config_data.source_chain} → {self.config_data.target_chain}"
                        f" ({token_amount_out_decimals} {self.token_obj.name})"
                        f" bridge transaction success: {tx_hash.hex()}")
                    return tx_hash.hex()
                else:
                    logger.error(f"Transaction is not success: {tx_hash.hex()}")

            else:
                logger.success(
                    f"[{self.config_data.source_chain} → {self.config_data.target_chain} "
                    f"({token_amount_out_decimals} {self.token_obj.name}) bridge transaction sent: {tx_hash.hex()}")
                return tx_hash.hex()
        except Exception as e:
            logger.error(f"Error while sending  transaction: {e}")
            return

    def transfer_from_core(self, private_key, wallet_number=None):
        if not self.token_obj:
            return

        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_token_balance_wei = self.get_token_balance(wallet_address=source_wallet_address,
                                                          token_contract=self.token_contract)
        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** self.get_token_decimals(self.token_contract)

        if self.config_data.send_to_one_address is True:
            dst_wallet_address = self.get_checksum_address(self.config_data.address_to_send)
        else:
            dst_wallet_address = wallet_address

        if self.config_data.send_all_balance is True:
            token_amount_out_wei = wallet_token_balance_wei
            if token_amount_out_wei == 0:
                logger.error(f"{self.config_data.source_coin_to_transfer} "
                             f"({self.config_data.source_chain}) balance is 0")
                return
        else:
            token_amount_out_wei = self.get_random_amount_out(min_amount=self.min_bridge_amount,
                                                              max_amount=self.max_bridge_amount,
                                                              token_contract=self.token_contract)

        token_amount_out_decimals = token_amount_out_wei / 10 ** self.get_token_decimals(self.token_contract)

        if wallet_token_balance_wei < token_amount_out_wei:
            logger.error(f"{self.config_data.source_coin_to_transfer} "
                         f"({self.config_data.source_chain})"
                         f" balance not enough "
                         f"to bridge. Balance: {wallet_token_balance_decimals}")
            return

        allowed_amount_to_bridge = self.check_allowance(wallet_address=wallet_address,
                                                        token_contract=self.token_contract,
                                                        spender=self.source_chain.router_address)

        if allowed_amount_to_bridge < token_amount_out_wei:
            logger.warning(
                f"Not enough allowance for {self.token_obj.name}, approving {self.token_obj.name} to bridge")

            token_approval = self.make_approve_for_token(private_key=private_key,
                                                         target_approve_amount=token_amount_out_wei,
                                                         token_contract=self.token_contract,
                                                         token_obj=self.token_obj,
                                                         spender=self.source_chain.router_address)

            if token_approval is not True:
                return
        else:
            logger.info(f"Wallet has enough allowance to bridge")

        txn = self.build_token_bridge_frome_core_tx(wallet_address=wallet_address,
                                                    amount_out=token_amount_out_wei,
                                                    token_obj=self.token_obj,
                                                    dst_wallet_address=dst_wallet_address)\

        try:
            estimated_gas_limit = self.get_estimate_gas(transaction=txn)

            if self.config_data.gas_limit > estimated_gas_limit:
                txn['gas'] = estimated_gas_limit

            if self.config_data.test_mode is True:
                logger.success(f"Estimated gas limit for "
                               f"{self.config_data.source_chain} → {self.config_data.target_chain} "
                               f"{self.token_obj.name} bridge: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            if self.config_data.wait_for_confirmation is True:
                time_out = self.config_data.confirmation_timeout_seconds
                tx_receipt = self.wait_for_tx_receipt(tx_hash=tx_hash, time_out=time_out)
                if tx_receipt['status'] == 1:
                    logger.success(
                        f"{self.config_data.source_chain} → {self.config_data.target_chain}"
                        f" ({token_amount_out_decimals} {self.token_obj.name})"
                        f" bridge transaction success: {tx_hash.hex()}")
                    return tx_hash.hex()
                else:
                    logger.error(f"Transaction is not success: {tx_hash.hex()}")

            else:
                logger.success(
                    f"{self.config_data.source_chain} → {self.config_data.target_chain}"
                    f" ({token_amount_out_decimals} {self.token_obj.name}) bridge transaction sent: {tx_hash.hex()}")
                return tx_hash.hex()
        except Exception as e:
            logger.error(f"Error while sending  transaction: {e}")
            return

