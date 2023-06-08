import time
import random

from typing import Union
from datetime import datetime, timedelta

from loguru import logger
from eth_account import Account
from web3 import Web3

from src.paths import CONTRACTS_DIR
from src.schemas.stake import AddLiquidityConfig, StakeStgConfig
from src.bridge_manager import BridgeManager, get_all_chain_paths, get_class_object_from_main_file


class StakeBase:
    def __init__(self, config: Union[AddLiquidityConfig, StakeStgConfig]):
        self.config_data = config
        self.all_chain_paths = get_all_chain_paths(CONTRACTS_DIR)
        self.source_chain = get_class_object_from_main_file(class_name=config.source_chain,
                                                            all_chain_paths=self.all_chain_paths)

        self.web3 = self.source_chain.web3

    def detect_coin(self, coin_query: str, chain_query: str):
        chain = get_class_object_from_main_file(class_name=chain_query,
                                                all_chain_paths=self.all_chain_paths)
        if not chain:
            return

        for coin in chain.token_contracts:
            if coin.name == coin_query:
                return coin

    def get_wallet_address(self, private_key):
        account = Account.from_key(private_key)
        return self.web3.to_checksum_address(account.address)

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

    def get_estimate_gas(self, transaction):
        estimated_gas_limit = self.source_chain.web3.eth.estimate_gas(transaction)
        return estimated_gas_limit

    def get_wallet_nonce(self, wallet_address):
        return self.web3.eth.get_transaction_count(wallet_address)

    def get_lock_period(self, lock_period_months):
        current_date = datetime.now()
        future_date = current_date + timedelta(days=lock_period_months * 30)
        timestamp = int(future_date.timestamp())
        return timestamp

    def get_random_amount_out(self, min_amount, max_amount, token_contract=None):
        random_amount = random.uniform(min_amount, max_amount)

        if token_contract is None:
            token_amount_out = Web3.to_wei(random_amount, 'ether')
        else:
            token_amount_out = int(round(random_amount, 3) * 10 ** self.get_token_decimals(token_contract))

        return token_amount_out

    def get_pool_id(self, token_obj):
        try:
            token_obj_pool_id = token_obj.pool_id
        except Exception as e:
            token_obj_pool_id = None

        return token_obj_pool_id

    def get_gas_price(self):
        if self.config_data.source_chain.lower() == 'arbitrum':
            return int(self.web3.eth.gas_price * 1.35)
        elif self.config_data.source_chain.lower() == 'polygon':
            return int(self.web3.eth.gas_price * 1.35)
        elif self.config_data.source_chain.lower() == 'avalanche':
            return int(self.web3.eth.gas_price * 1.15)
        else:
            return self.web3.eth.gas_price

    def allowance_check_loop(self, wallet_address, target_allowance_amount, token_contract, spender):
        process_start_time = time.time()
        while True:
            if time.time() - process_start_time > 150:
                return False

            current_allowance = self.check_allowance(wallet_address=wallet_address,
                                                     token_contract=token_contract,
                                                     spender=spender)
            logger.debug(f"Waiting allowance txn, allowance: {current_allowance}, need: {target_allowance_amount}, "
                         f"time passed: {time.time() - process_start_time}, will wait 150 seconds then skip wallet" )

            if current_allowance >= target_allowance_amount:
                return True
            time.sleep(3)

    def make_approve_for_token(self, private_key, target_approve_amount, token_contract, token_obj, spender):
        wallet_address = self.get_wallet_address(private_key)
        approve_amount = int((10 ** 8) * 10 ** self.get_token_decimals(token_contract))
        allowance_txn = self.build_allowance_tx(wallet_address=wallet_address,
                                                token_contract=token_contract,
                                                amount_out=approve_amount,
                                                spender=spender)
        try:
            estimate_gas_limit = self.get_estimate_gas(allowance_txn)

            if estimate_gas_limit < self.config_data.gas_limit:
                allowance_txn['gas'] = estimate_gas_limit

            if self.config_data.test_mode is True:
                logger.info(f"[{wallet_address}] - Estimated gas limit for {token_obj.name}"
                            f" approve: {estimate_gas_limit}. You are currently in test mode")
                return

            signed_txn = self.web3.eth.account.sign_transaction(allowance_txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.success(f"[{wallet_address}] - Approve transaction sent: {tx_hash.hex()}")
            time.sleep(0.2)

            allowance_check = self.allowance_check_loop(wallet_address=wallet_address,
                                                        target_allowance_amount=target_approve_amount,
                                                        token_contract=token_contract,
                                                        spender=spender)
            if allowance_check is True:
                logger.info(f"[{wallet_address}] - Approve transaction confirmed")
                time.sleep(2)
                return True
            else:
                logger.info(f"[{wallet_address}] - Allowance process took more than 150 seconds, aborting")
                return False

        except Exception as e:
            logger.error(f"[{wallet_address}] - Error while approving txn: {e}")
            return False

    def build_allowance_tx(self, wallet_address, token_contract, amount_out, spender):
        nonce = self.get_wallet_nonce(wallet_address=wallet_address)
        gas_price = self.get_gas_price()
        gas_limit = self.config_data.gas_limit
        allowance_transaction = token_contract.functions.approve(
            spender,
            int(amount_out)
        ).build_transaction({
            'from': wallet_address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        return allowance_transaction

    def build_add_liquidity_txn(self, wallet_address, token_obj, amount_to_stake):
        nonce = self.get_wallet_nonce(wallet_address=wallet_address)
        gas_price = self.get_gas_price()
        gas_limit = self.config_data.gas_limit
        pool_id = self.get_pool_id(token_obj=token_obj)
        stake_transaction = self.source_chain.router_contract.functions.addLiquidity(
            pool_id,
            amount_to_stake,
            wallet_address
        ).build_transaction({
            'from': wallet_address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        return stake_transaction

    def build_stg_stake_txn(self, wallet_address, amount_to_stake, lock_period):
        nonce = self.get_wallet_nonce(wallet_address=wallet_address)
        gas_price = self.get_gas_price()
        gas_limit = self.config_data.gas_limit
        stake_transaction = self.source_chain.voting_contract.functions.create_lock(
            amount_to_stake,
            lock_period
        ).build_transaction({
            'from': wallet_address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        return stake_transaction
