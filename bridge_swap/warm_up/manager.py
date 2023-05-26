import math
import random
import os
import json
import time

from typing import List
import datetime

from src.schemas.config import WarmUpConfigSchema
from src.schemas.warmup_wallet import WarmUpWalletSchema
from src.bridge_manager import find_classes_in_packages
from src.paths import CONTRACTS_DIR, WALLET_LOGS_DIR
from contracts.contracts_base import ContractsBase

from loguru import logger
from eth_account import Account


class WarmUpManager:
    def __init__(self, config: WarmUpConfigSchema):
        self.all_chains_obj: list = find_classes_in_packages(CONTRACTS_DIR, ContractsBase)
        self.chain_options: List[str] = config.chain_options
        self.stable_coin_names: List[str] = ['USDC', 'USDT', 'DAI']

    def detect_chain(self, chain_query: str):
        for chain_obj in self.all_chains_obj:
            chain = chain_obj()
            if chain.name.lower() == chain_query.lower():
                return chain

    def detect_coin(self, coin_query: str, chain_query: str):
        chain = self.detect_chain(chain_query)
        if not chain:
            return

        for coin in chain.token_contracts:
            if coin.name.lower() == coin_query.lower():
                return coin

    def get_wallet_address(self, private_key: str):
        try:
            num_of_chains = len(self.all_chains_obj)
            chain_index = random.randint(0, num_of_chains - 1)
            account = Account.from_key(private_key)
            return account.address
        except Exception as e:
            logger.error(f'Error while getting wallet address: {e}')

    def get_random_amount(self, min_amount, max_amount):
        return random.uniform(min_amount, max_amount)

    def get_eth_balance(self, chain_web3, wallet_address):
        balance = chain_web3.eth.get_balance(wallet_address)
        return balance

    def get_token_decimals(self, token_contract):
        decimals = token_contract.functions.decimals().call()
        return decimals

    def get_token_balance(self, chain_web3, token_obj, wallet_address):
        token_contract = chain_web3.eth.contract(address=token_obj.address, abi=token_obj.abi)
        balance = token_contract.functions.balanceOf(wallet_address).call()
        return balance

    def fetch_wallet_chain_balances(self, wallet_address: str):

        logger.info(f'[{wallet_address}] - Fetching wallet balances')
        wallet_chain_balances = {"wallet_address": wallet_address}
        for chain in self.chain_options:
            chain_obj = self.detect_chain(chain)
            chain_web3 = chain_obj.web3
            chain_balance = {}
            if not chain_obj:
                continue

            if chain_obj.is_eth_available is True:
                eth_balance_wei = self.get_eth_balance(chain_web3=chain_web3,
                                                       wallet_address=wallet_address)
                eth_balance = chain_web3.from_wei(eth_balance_wei, 'ether')
                chain_balance['Ethereum'] = float(eth_balance)

            for stable_coin in self.stable_coin_names:
                coin_obj = self.detect_coin(stable_coin, chain_obj.name)
                if not coin_obj:
                    continue
                stable_coin_balance_wei = self.get_token_balance(chain_web3=chain_web3,
                                                                 token_obj=coin_obj,
                                                                 wallet_address=wallet_address)
                if stable_coin_balance_wei == 0:
                    continue
                token_contract = chain_web3.eth.contract(address=coin_obj.address, abi=coin_obj.abi)
                stable_coin_balance = stable_coin_balance_wei / math.pow(10, self.get_token_decimals(token_contract=token_contract))

                chain_balance[coin_obj.name] = stable_coin_balance

            wallet_chain_balances[chain_obj.name] = chain_balance

        logger.info(f'[{wallet_address}] - Wallet balances fetched')
        for chain_balance in wallet_chain_balances:
            logger.info(f'{chain_balance}: {wallet_chain_balances[chain_balance]}')
        return wallet_chain_balances


class WalletManager:
    def __init__(self, private_key: str):
        self.private_key = private_key
        account = Account.from_key(private_key)
        self.wallet_address = account.address
        self.wallet_log_file_dir = self.get_wallet_dir(file_name=self.wallet_address)

    def build_wallet_data(self, data: dict = None) -> WarmUpWalletSchema:
        if data is None:
            wallet_data: WarmUpWalletSchema = WarmUpWalletSchema(
                address=self.wallet_address,
                private_key=self.private_key,
            )
            return wallet_data
        else:
            if 'address' not in data:
                data['address'] = self.wallet_address
            if 'private_key' not in data:
                data['private_key'] = self.private_key
            wallet_data: WarmUpWalletSchema = WarmUpWalletSchema(**data)
            return wallet_data

    def update_wallet_log_file(self, data: dict = None):
        try:
            with open(self.wallet_log_file_dir, 'w') as f:
                if data is None:
                    wallet_data = self.build_wallet_data()
                    json.dump(wallet_data.dict(), f, indent=4)
                    logger.info(f'{self.wallet_address} - wallet log file updated with no info in local directory')
                else:
                    wallet_data = self.build_wallet_data(data=data)
                    json.dump(wallet_data.dict(), f, indent=4)
                    logger.info(f'{self.wallet_address} - wallet log file updated with info in local directory')

        except FileNotFoundError:
            logger.error(f'{self.wallet_address} - wallet log file not found in local directory')
            self.create_wallet_log_file()

    def create_wallet_log_file(self):
        try:
            with open(self.wallet_log_file_dir, 'w') as f:
                wallet_data = self.build_wallet_data()
                json.dump(wallet_data.dict(), f, indent=4)
                logger.info(f'[{self.wallet_address}] - wallet log file created in local directory')
        except FileNotFoundError:
            logger.error(f'[{self.wallet_address}] - wallet log file not found in local directory')

    def get_wallet_data(self):
        try:
            with open(self.wallet_log_file_dir, 'r') as f:
                wallet_data = json.load(f)
                if not wallet_data:
                    self.update_wallet_log_file()
                    return self.get_wallet_data()
                return WarmUpWalletSchema(**wallet_data)
        except FileNotFoundError:
            logger.error(f'[{self.wallet_address}] - wallet log file not found in local directory')

    def get_wallet_dir(self, file_name: str):
        try:
            wallet_logs_dir = WALLET_LOGS_DIR
            file_name = f'{file_name}.json'
            wallet_logs_file_path = os.path.join(wallet_logs_dir, file_name)
            return wallet_logs_file_path
        except Exception as e:
            logger.error(f'Error while getting wallet dir: {e}')

    def check_if_wallet_has_log_file(self):
        try:
            with open(self.wallet_log_file_dir, 'r') as f:
                wallet_data = json.load(f)
                if not wallet_data:
                    logger.warning(f'[{self.wallet_address}] - wallet log file not found in local directory')
                    return False
                return True
        except FileNotFoundError:
            logger.warning(f'[{self.wallet_address}] - wallet log file not found in local directory')
            return False

    def initiate_wallet(self):
        if self.check_if_wallet_has_log_file() is False:
            self.create_wallet_log_file()
            return False
        else:
            return True


