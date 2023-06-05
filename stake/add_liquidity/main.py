import time
import random

from typing import Union
from datetime import datetime, timedelta

from loguru import logger

from src.schemas.stake import AddLiquidityConfig
from stake.stake_base import StakeBase
from src.config import print_config, get_add_liquidity_config
from src.rpc_manager import RpcValidator
from src.files_manager import read_evm_wallets_from_file


def mass_add_liquidity(config: AddLiquidityConfig):
    print_config(config=config)

    rpc_validator = RpcValidator()
    rpcs = rpc_validator.validated_rpcs

    wallets = read_evm_wallets_from_file()
    liquidity_stg = LiquidityStargate(config=config)

    wallets_amount = len(wallets)
    wallet_number = 1
    for wallet in wallets:
        add_liquidity_status = liquidity_stg.add_liquidity(private_key=wallet)

        if wallet_number == wallets_amount:
            logger.info(f"Add liquidity process is finished\n")
            break

        wallet_number += 1

        if add_liquidity_status is not None:
            time_delay = random.randint(config.min_delay_seconds, config.max_delay_seconds)
        else:
            time_delay = 3

        if time_delay == 0:
            time.sleep(0.3)
            continue

        delta = timedelta(seconds=time_delay)
        result_datetime = datetime.now() + delta

        logger.info(f"Waiting {time_delay} seconds, next wallet bridge {result_datetime}\n")
        time.sleep(time_delay)


class LiquidityStargate(StakeBase):
    def __init__(self, config: Union[AddLiquidityConfig]):
        super().__init__(config=config)
        self.token_obj = self.detect_coin(coin_query=self.config_data.coin_to_stake,
                                          chain_query=self.config_data.source_chain)
        self.token_contract = self.web3.eth.contract(address=self.token_obj.address,
                                                     abi=self.token_obj.abi)

    def add_liquidity(self, private_key):
        if not self.token_obj:
            return

        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_token_balance_wei = self.get_token_balance(wallet_address=source_wallet_address,
                                                          token_contract=self.token_contract)
        wallet_token_balance = wallet_token_balance_wei / 10 ** self.get_token_decimals(self.token_contract)

        if self.config_data.stake_all_balance is True:
            token_amount_to_stake = wallet_token_balance_wei
            if token_amount_to_stake == 0:
                logger.error(f"[{source_wallet_address}] - {self.config_data.coin_to_stake} "
                             f"({self.config_data.source_chain}) balance is 0")
                return
        else:
            if self.config_data.max_amount_to_stake > wallet_token_balance:
                max_amount_to_stake = wallet_token_balance
            else:
                max_amount_to_stake = self.config_data.max_amount_to_stake

            token_amount_to_stake = self.get_random_amount_out(min_amount=self.config_data.min_amount_to_stake,
                                                               max_amount=max_amount_to_stake,
                                                               token_contract=self.token_contract)

        token_amount_out_to_stake_decimals = token_amount_to_stake / 10 ** self.get_token_decimals(self.token_contract)

        if wallet_token_balance_wei < token_amount_to_stake:
            logger.error(f"[{source_wallet_address}] - {self.config_data.coin_to_stake} "
                         f"({self.config_data.source_chain})"
                         f" balance not enough "
                         f"to add liquidity. Balance: {wallet_token_balance}. Need: {token_amount_out_to_stake_decimals}")
            return

        allowed_amount_to_bridge = self.check_allowance(wallet_address=source_wallet_address,
                                                        token_contract=self.token_contract,
                                                        spender=self.source_chain.router_address)

        if allowed_amount_to_bridge < token_amount_to_stake:
            logger.warning(
                f"[{source_wallet_address}] - Not enough allowance for {self.token_obj.name},"
                f" approving {self.token_obj.name} to add liquidity")

            token_approval = self.make_approve_for_token(private_key=private_key,
                                                         target_approve_amount=token_amount_to_stake,
                                                         token_contract=self.token_contract,
                                                         token_obj=self.token_obj,
                                                         spender=self.source_chain.router_address)
            if token_approval is not True:
                return
        else:
            logger.info(f"[{source_wallet_address}] - Wallet has enough allowance to add liquidity")

        add_liquidity_txn = self.build_add_liquidity_txn(amount_to_stake=token_amount_to_stake,
                                                         wallet_address=source_wallet_address,
                                                         token_obj=self.token_obj)

        if add_liquidity_txn is None:
            logger.error(f"[{source_wallet_address}] - Failed to build transaction,"
                         f" please check your chain and coin add liquidity options")
            return

        try:
            pre_estimated_gas_limit = self.get_estimate_gas(transaction=add_liquidity_txn)
            if self.config_data.gas_limit > pre_estimated_gas_limit:
                add_liquidity_txn['gas'] = pre_estimated_gas_limit

            estimated_gas_limit = self.get_estimate_gas(transaction=add_liquidity_txn)

            if self.config_data.test_mode is True:
                logger.info(f"[{source_wallet_address}] - Estimated gas limit for add {token_amount_out_to_stake_decimals}"
                            f"{self.token_obj.name} ({self.config_data.source_chain}) liquidity:"
                            f": {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(add_liquidity_txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.success(
                f"[{source_wallet_address}] - {self.config_data.source_chain} add {token_amount_out_to_stake_decimals}"
                f"{self.token_obj.name} ({self.config_data.source_chain}) liquidity transaction sent: {tx_hash.hex()}")

            return tx_hash.hex()
        except Exception as e:
            logger.error(f"[{source_wallet_address}] - Error while sending add liquidity transaction: {e}")
            return


if __name__ == '__main__':
    mass_add_liquidity(config=get_add_liquidity_config())