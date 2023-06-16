import time
import random

from typing import Union
from datetime import datetime, timedelta

from loguru import logger

from src.schemas.stake import StakeStgConfig
from stake.stake_base import StakeBase
from src.config import print_config
from src.rpc_manager import RpcValidator
from src.files_manager import read_evm_wallets_from_file


def mass_stake_stg(config: StakeStgConfig):
    print_config(config=config)

    rpc_validator = RpcValidator()
    rpcs = rpc_validator.validated_rpcs

    wallets = read_evm_wallets_from_file()
    staker = StgStake(config=config)

    wallets_amount = len(wallets)
    wallet_number = 1
    for wallet in wallets:
        blured_wallet = staker.blur_private_key(private_key=wallet)
        wallet_address = staker.get_wallet_address(private_key=wallet)
        logger.info(f"[{wallet_number}] - {wallet_address}")
        logger.info(f"Got wallet pk /{blured_wallet}/")

        stake_stg_status = staker.stake_stg(private_key=wallet)

        if wallet_number == wallets_amount:
            logger.info(f"Stake process is finished\n")
            break

        wallet_number += 1

        if stake_stg_status is not None:
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


class StgStake(StakeBase):
    def __init__(self, config: Union[StakeStgConfig]):
        super().__init__(config=config)
        self.token_obj = self.detect_coin(coin_query='STG',
                                          chain_query=self.config_data.source_chain)
        self.token_contract = self.web3.eth.contract(address=self.token_obj.address,
                                                     abi=self.token_obj.abi)

    def stake_stg(self, private_key):
        if not self.token_obj:
            return

        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_token_balance_wei = self.get_token_balance(wallet_address=source_wallet_address,
                                                          token_contract=self.token_contract)

        wallet_token_balance = wallet_token_balance_wei / 10 ** self.get_token_decimals(self.token_contract)

        if self.config_data.stake_all_balance is True:
            stg_amount_to_stake = wallet_token_balance_wei
            if stg_amount_to_stake == 0:
                logger.error(f"{self.token_obj.name} ({self.config_data.source_chain}) balance is 0")
                return
        else:
            if self.config_data.max_amount_to_stake > wallet_token_balance:
                max_amount_to_stake = wallet_token_balance
            else:
                max_amount_to_stake = self.config_data.max_amount_to_stake

            stg_amount_to_stake = self.get_random_amount_out(min_amount=self.config_data.min_amount_to_stake,
                                                             max_amount=max_amount_to_stake,
                                                             token_contract=self.token_contract)

        stg_amount_to_stake_decimals = stg_amount_to_stake / 10 ** self.get_token_decimals(self.token_contract)

        if wallet_token_balance_wei < stg_amount_to_stake:
            logger.error(f"{self.token_obj.name} ({self.config_data.source_chain})"
                         f" balance not enough "
                         f"to bridge. Balance: {wallet_token_balance}. Need: {stg_amount_to_stake_decimals}")
            return

        allowed_amount_to_bridge = self.check_allowance(wallet_address=source_wallet_address,
                                                        token_contract=self.token_contract,
                                                        spender=self.source_chain.voting_address)

        if allowed_amount_to_bridge < stg_amount_to_stake:
            logger.warning(
                f"Not enough allowance for {self.token_obj.name}, approving {self.token_obj.name} to stake")

            token_approval = self.make_approve_for_token(private_key=private_key,
                                                         target_approve_amount=stg_amount_to_stake,
                                                         token_contract=self.token_contract,
                                                         token_obj=self.token_obj,
                                                         spender=self.source_chain.voting_address)

            if token_approval is not True:
                return
        else:
            logger.info(f"Wallet has enough allowance to stake")

        lock_period_stamp = self.get_lock_period(self.config_data.lock_period_months)

        stake_txn = self.build_stg_stake_txn(wallet_address=source_wallet_address,
                                             amount_to_stake=stg_amount_to_stake,
                                             lock_period=lock_period_stamp)

        if stake_txn is None:
            logger.error(f"Failed to build transaction,"
                         f" please check your chain and STG stake options")
            return

        try:
            pre_estimated_gas_limit = self.get_estimate_gas(transaction=stake_txn)
            if self.config_data.gas_limit > pre_estimated_gas_limit:
                stake_txn['gas'] = pre_estimated_gas_limit

            estimated_gas_limit = self.get_estimate_gas(transaction=stake_txn)

            if self.config_data.test_mode is True:
                logger.info(f"Estimated gas limit for stake {stg_amount_to_stake_decimals}"
                            f"{self.token_obj.name} ({self.config_data.source_chain}):"
                            f" {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(stake_txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            if self.config_data.wait_for_confirmation is True:
                time_out = self.config_data.confirmation_timeout_seconds
                tx_receipt = self.wait_for_tx_receipt(tx_hash=tx_hash, time_out=time_out)
                if tx_receipt['status'] == 1:
                    logger.success(
                        f"Stake {stg_amount_to_stake_decimals} "
                        f"{self.token_obj.name} ({self.config_data.source_chain}) transaction success: {tx_hash.hex()}")
                    return tx_hash.hex()
                else:
                    logger.error(f"Transaction is not success: {tx_hash.hex()}")

            else:
                logger.success(
                    f"Stake {stg_amount_to_stake_decimals} "
                    f"{self.token_obj.name} ({self.config_data.source_chain}) transaction sent: {tx_hash.hex()}")
                return tx_hash.hex()

        except Exception as e:
            logger.error(f"Error while sending STG stake transaction: {e}")
            return
