import os
import importlib.util

from contracts.contracts_base import ContractsBase

from src.schemas.config import ConfigSchema, WarmUpConfigSchema
from src.paths import CONTRACTS_DIR
from src.files_manager import read_evm_wallets_from_file, read_aptos_wallets_from_file


def find_classes_in_main_file(main_path, base_class):
        module_name = os.path.splitext(os.path.basename(main_path))[0]
        module_spec = importlib.util.spec_from_file_location(module_name, main_path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        classes = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, base_class) and obj is not base_class:
                classes.append(obj)

        return classes


def find_classes_in_packages(directory, base_class):
        package_dirs = [x[0] for x in os.walk(directory) if '__init__.py' in x[2]]
        classes = []
        for package_dir in package_dirs:
            main_path = os.path.join(package_dir, 'main.py')
            if os.path.isfile(main_path):
                package_classes = find_classes_in_main_file(main_path, base_class)
                classes.extend(package_classes)

        return classes


class BridgeManager:
    def __init__(self, input_data: ConfigSchema):
        self.input_data = input_data
        self.source_chain = self.input_data.source_chain
        self.target_chain = self.input_data.target_chain
        self.coin_to_transfer = self.input_data.coin_to_transfer

        self.aptos_wallets: list = read_aptos_wallets_from_file()
        self.evm_wallets = read_evm_wallets_from_file()

    def detect_chain(self, chain_query: str):
        all_chains_obj: list = find_classes_in_packages(CONTRACTS_DIR, ContractsBase)
        for chain_obj in all_chains_obj:
            chain = chain_obj()
            if chain.name == chain_query:
                return chain

    def detect_coin(self, coin_query: str, chain_query: str):
        chain = self.detect_chain(chain_query)
        if not chain:
            return

        for coin in chain.token_contracts:
            if coin.name == coin_query:
                return coin

    def aptos_handler(self):
        usdc_aptos_eligible_chains = ['Arbitrum', 'Optimism', 'Ethereum', 'Avalanche', 'Polygon']
        usdt_aptos_eligible_chains = ['BSC', 'Ethereum', 'Avalanche', 'Polygon']
        eth_aptos_eligible_chains = ['Arbitrum', 'Optimism', 'Ethereum']

        if self.input_data.send_to_one_address is True:
            if len(self.input_data.address_to_send) != 66:
                error_msg = f'Invalid address to send'
                return error_msg

        if self.input_data.send_to_one_address is False:
            if len(self.aptos_wallets) == 0:
                error_msg = f'No Aptos wallets found in aptos_addresses.txt'
                return error_msg

            if len(self.evm_wallets) != len(self.aptos_wallets):
                error_msg = f'Number of EVM wallets and Aptos wallets must be the same'
                return error_msg

        if self.coin_to_transfer == 'USDC':
            if self.source_chain not in usdc_aptos_eligible_chains:
                error_msg = f'USDC bridge from {self.source_chain} to {self.target_chain} is not supported'
                return error_msg

        if self.coin_to_transfer == 'USDT':
            if self.source_chain not in usdt_aptos_eligible_chains:
                error_msg = f'USDT bridge from {self.source_chain} to {self.target_chain} is not supported'
                return error_msg

        if self.coin_to_transfer == 'Ethereum':
            if self.source_chain not in eth_aptos_eligible_chains:
                error_msg = f'Ethereum bridge from {self.source_chain} to {self.target_chain} is not supported'
                return error_msg

        return True

    def stargate_handler(self):
        eth_eligible_chains = ['Optimism', 'Ethereum', 'Arbitrum']
        usdc_eligible_chains = ['Arbitrum', 'Optimism', 'Ethereum', 'Avalanche', 'Polygon', 'Fantom']
        usdt_eligible_chains = ['Arbitrum', 'Ethereum', 'BSC', 'Avalanche', 'Polygon']

        if self.input_data.send_to_one_address is True:
            if len(self.input_data.address_to_send) != 42:
                error_msg = f'Invalid address to send'
                return error_msg

        if self.coin_to_transfer == 'Ethereum':
            if self.target_chain not in eth_eligible_chains:
                error_msg = f'Ethereum bridge from {self.source_chain} to {self.target_chain} is not supported'
                return error_msg

            if self.source_chain not in eth_eligible_chains:
                error_msg = f'Ethereum bridge from {self.source_chain} to {self.target_chain} is not supported'
                return error_msg

        if self.coin_to_transfer == 'USDC':
            error_msg = f'USDC bridge from {self.source_chain} to {self.target_chain} is not supported'
            if self.source_chain not in usdc_eligible_chains:
                return error_msg

        if self.coin_to_transfer == 'USDT':
            if self.source_chain not in usdt_eligible_chains:
                error_msg = f'USDT bridge from {self.source_chain} to {self.target_chain} is not supported'
                return error_msg

        return True

    def core_dao_handler(self):
        usdc_eligible_chains = ['BSC', 'CoreDao']
        usdt_eligible_chains = ['BSC', 'CoreDao']

        if self.input_data.send_to_one_address is True:
            if len(self.input_data.address_to_send) != 42:
                error_msg = f'Invalid address to send'
                return error_msg

        if self.coin_to_transfer == 'USDC':
            error_msg = f'USDC bridge from {self.source_chain} to {self.target_chain} is not supported'
            if self.source_chain not in usdc_eligible_chains:
                return error_msg

        if self.coin_to_transfer == 'USDT':
            if self.source_chain not in usdt_eligible_chains:
                error_msg = f'USDT bridge from {self.source_chain} to {self.target_chain} is not supported'
                return error_msg

        return True

    def common_fields_check(self):
        if self.input_data.send_all_balance is False:
            if self.check_if_float_valid(self.input_data.min_bridge_amount) is False:
                error_msg = 'Min bridge amount is not valid'
                return error_msg

            if self.check_if_float_valid(self.input_data.max_bridge_amount) is False:
                error_msg = 'Max bridge amount is not valid'
                return error_msg

        if self.input_data.min_bridge_amount > self.input_data.max_bridge_amount:
            error_msg = 'Min bridge amount is greater than max bridge amount'
            return error_msg

        if self.check_if_float_valid(self.input_data.gas_limit) is False:
            error_msg = 'Gas limit is not valid'
            return error_msg

        if self.check_if_slippage_valid() is False:
            error_msg = 'Slippage is not valid, should be between 0.1 and 100'
            return error_msg

        if self.input_data.custom_gas_price is True:
            if self.check_if_float_valid(self.input_data.gas_price) is False:
                error_msg = 'Gas price is not valid'
                return error_msg

        if self.input_data.min_delay_seconds > self.input_data.max_delay_seconds:
            error_msg = 'Min delay seconds is greater than max delay seconds'
            return error_msg

        if self.input_data.min_delay_seconds < 0:
            error_msg = 'Min delay seconds is less than 0'
            return error_msg

        if self.input_data.max_delay_seconds < 0:
            error_msg = 'Max delay seconds is less than 0'
            return error_msg

        return True

    def check_if_slippage_valid(self):
        try:
            slippage = float(self.input_data.slippage)
            if 0 < slippage <= 100:
                return True
            else:
                return False
        except ValueError:
            return False

    def check_if_float_valid(self, value):
        try:
            value = float(value)
            if value > 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def check_if_route_eligible(self):
        if len(self.evm_wallets) == 0:
            error_msg = f'No EVM wallets found in evm_wallets.txt'
            return error_msg

        if not self.input_data.source_chain:
            error_msg = 'Source chain is not specified'
            return error_msg

        if not self.input_data.target_chain:
            error_msg = 'Target chain is not specified'
            return error_msg

        if self.source_chain == self.target_chain:
            error_msg = f'Bridge from {self.source_chain} to {self.target_chain} is not supported'
            return error_msg

        if self.input_data.bridge_option == 'Aptos':
            aptos_eligibility = self.aptos_handler()
            if aptos_eligibility is not True:
                return aptos_eligibility

        if self.input_data.bridge_option == 'Stargate':
            evm_eligibility = self.stargate_handler()
            if evm_eligibility is not True:
                return evm_eligibility

        if self.input_data.bridge_option == 'CoreDao':
            core_eligibility = self.core_dao_handler()
            if core_eligibility is not True:
                return core_eligibility

        common_eligibility = self.common_fields_check()
        if common_eligibility is not True:
            return common_eligibility

        return True


class WarmUpRouteValidator:
    def __init__(self, input_data: WarmUpConfigSchema):
        self.config = input_data

    def check_if_chain_options_valid(self):
        chain_options = self.config.chain_options

        if len(chain_options) < 2:
            error_msg = f'Choose at least 2 chains'
            return error_msg

        return True

    def check_if_chain_eth_compatible(self):
        eth_eligible_chains = ['Optimism', 'Ethereum', 'Arbitrum']
        for chain in self.config.chain_options:
            if chain not in eth_eligible_chains:
                error_msg = f'ETH bridge is not supported on {chain.upper()}'
                return error_msg

        return True

    def check_if_delay_valid(self):
        min_delay = self.config.min_delay_seconds
        max_delay = self.config.max_delay_seconds

        try:
            min_delay = int(min_delay)
            max_delay = int(max_delay)

            if min_delay < 0 or max_delay < 0:
                error_msg = f'Delay should be positive'
                return error_msg

            if min_delay > max_delay:
                error_msg = f'Min delay should be less than max delay'
                return error_msg

            return True

        except ValueError:
            error_msg = f'Delay should be integer valid'
            return error_msg

    def check_if_amount_valid(self):
        min_amount = self.config.min_amount_to_transfer
        max_amount = self.config.max_amount_to_transfer

        try:
            min_amount = float(min_amount)
            max_amount = float(max_amount)

        except ValueError:
            error_msg = f'Amount should be float valid'
            return error_msg

        if min_amount <= 0 or max_amount <= 0:
            error_msg = f'Min and Max transfer amount should be > 0'
            return error_msg

        if min_amount > max_amount:
            error_msg = f'Min amount should be less than max amount'
            return error_msg

        return True

    def check_if_gas_limit_valid(self):
        gas_limit = self.config.max_gas_limit

        try:
            gas_limit = int(gas_limit)

        except ValueError:
            error_msg = f'Gas limit should be integer valid'
            return error_msg

        if gas_limit < 0:
            error_msg = f'Gas limit should be positive'
            return error_msg

        return True

    def check_of_slippage_valid(self):
        slippage = self.config.slippage
        try:
            slippage = float(slippage)
        except ValueError:
            error_msg = f'Slippage should be float valid'
            return error_msg

        if slippage < 0.1 or slippage > 100:
            error_msg = f'Slippage should be between 0 and 100'
            return error_msg

        return True

    def check_route(self):
        if len(read_evm_wallets_from_file()) == 0:
            error_msg = f'No EVM wallets found in evm_wallets.txt'
            return error_msg

        if self.check_if_chain_options_valid() is not True:
            return self.check_if_chain_options_valid()

        if self.config.coin_to_transfer.lower() == 'ethereum':
            eth_eligibility = self.check_if_chain_eth_compatible()
            if eth_eligibility is not True:
                return eth_eligibility

        if self.check_if_delay_valid() is not True:
            return self.check_if_delay_valid()

        if self.check_if_amount_valid() is not True:
            return self.check_if_amount_valid()

        if self.check_if_gas_limit_valid() is not True:
            return self.check_if_gas_limit_valid()

        if self.check_of_slippage_valid() is not True:
            return self.check_of_slippage_valid()

        return True

