import time
import random

from datetime import datetime, timedelta

from bridge_swap.base_bridge import BridgeBase
from src.files_manager import read_evm_wallets_from_file
from src.schemas.config import ConfigSchema
from src.config import print_config
from src.rpc_manager import RpcValidator

from loguru import logger


def token_mass_transfer(config_data: ConfigSchema):
    print_config(config=config_data)

    rpc_validator = RpcValidator()
    rpcs = rpc_validator.validated_rpcs

    wallets = read_evm_wallets_from_file()
    token_bridge = TokenBridgeManual(config=config_data)
    wallet_number = 1
    wallets_amount = len(wallets)
    for wallet in wallets:
        bridge_status = token_bridge.transfer(private_key=wallet, wallet_number=wallet_number)

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


class TokenBridgeManual(BridgeBase):
    def __init__(self, config: ConfigSchema):
        super().__init__(config=config)
        self.src_token_obj = self.bridge_manager.detect_coin(coin_query=config.source_coin_to_transfer,
                                                             chain_query=self.config_data.source_chain)
        self.src_token_contract = self.web3.eth.contract(address=self.src_token_obj.address,
                                                         abi=self.src_token_obj.abi)

        if config.target_coin_to_transfer is None:
            dst_coin_name = self.get_dst_coin_name(src_token_obj=self.src_token_obj)
        else:
            dst_coin_name = config.target_coin_to_transfer

        self.dst_token_obj = self.bridge_manager.detect_coin(coin_query=dst_coin_name,
                                                             chain_query=self.config_data.target_chain)
        self.dst_token_contract = self.web3.eth.contract(address=self.dst_token_obj.address,
                                                         abi=self.dst_token_obj.abi)

    def transfer(self, private_key, wallet_number=None):
        if not self.src_token_obj or not self.dst_token_obj:
            return

        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_token_balance_wei = self.get_token_balance(wallet_address=source_wallet_address,
                                                          token_contract=self.src_token_contract)
        wallet_token_balance = wallet_token_balance_wei / 10 ** self.get_token_decimals(self.src_token_contract)

        if self.config_data.send_to_one_address is True:
            dst_wallet_address = self.get_checksum_address(self.config_data.address_to_send)
        else:
            dst_wallet_address = wallet_address

        wallet_number = self.get_wallet_number(wallet_number=wallet_number)

        if self.config_data.send_all_balance is True:
            token_amount_out = wallet_token_balance_wei
            if token_amount_out == 0:
                logger.error(f"{wallet_number} [{source_wallet_address}] - {self.config_data.source_coin_to_transfer} "
                             f"({self.config_data.source_chain}) balance is 0")
                return
        else:
            token_amount_out = self.get_random_amount_out(min_amount=self.min_bridge_amount,
                                                          max_amount=self.max_bridge_amount,
                                                          token_contract=self.src_token_contract)

        token_amount_out_decimals = token_amount_out / 10 ** self.get_token_decimals(self.src_token_contract)

        if wallet_token_balance_wei < token_amount_out:
            logger.error(f"{wallet_number} [{source_wallet_address}] - {self.config_data.source_coin_to_transfer} "
                         f"({self.config_data.source_chain})"
                         f" balance not enough "
                         f"to bridge. Balance: {wallet_token_balance}. Need: {token_amount_out_decimals}")
            return

        allowed_amount_to_bridge = self.check_allowance(wallet_address=wallet_address,
                                                        token_contract=self.src_token_contract,
                                                        spender=self.source_chain.router_address)

        if allowed_amount_to_bridge < token_amount_out:
            logger.warning(
                f"{wallet_number} [{source_wallet_address}] - Not enough allowance for {self.src_token_obj.name},"
                f" approving {self.src_token_obj.name} to bridge")

            token_approval = self.make_approve_for_token(private_key=private_key,
                                                         target_approve_amount=token_amount_out,
                                                         token_contract=self.src_token_contract,
                                                         token_obj=self.src_token_obj,
                                                         spender=self.source_chain.router_address)
            if token_approval is not True:
                return
        else:
            logger.info(f"{wallet_number} [{source_wallet_address}] - Wallet has enough allowance to bridge")

        txn = self.build_token_bridge_tx(wallet_address=wallet_address,
                                         dst_wallet_address=dst_wallet_address,
                                         src_token_obj=self.src_token_obj,
                                         dst_token_obj=self.dst_token_obj,
                                         amount_out=token_amount_out,
                                         chain_id=self.target_chain.chain_id)

        if txn is None:
            logger.error(f"{wallet_number} [{source_wallet_address}] - Failed to build transaction,"
                         f" please check your chain and coin bridge options")
            return

        try:
            pre_estimated_gas_limit = self.get_estimate_gas(transaction=txn)
            if self.config_data.gas_limit > pre_estimated_gas_limit:
                txn['gas'] = pre_estimated_gas_limit

            estimated_gas_limit = self.get_estimate_gas(transaction=txn)

            if self.config_data.test_mode is True:
                logger.info(f"{wallet_number} [{source_wallet_address}] - Estimated gas limit for "
                            f"|{self.config_data.source_chain} → {self.config_data.target_chain}|, "
                            f"{token_amount_out_decimals} ({self.src_token_obj.name} → {self.dst_token_obj.name})"
                            f" bridge: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.success(
                f"{wallet_number}"
                f" [{source_wallet_address}] - {self.config_data.source_chain} → {self.config_data.target_chain} "
                f"{token_amount_out_decimals} {self.src_token_obj.name} bridge transaction sent: {tx_hash.hex()}")

            return tx_hash.hex()
        except Exception as e:
            logger.error(f"{wallet_number} [{source_wallet_address}] - Error while sending  transaction: {e}")
            return
