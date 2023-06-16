from src.schemas.stake import StakeStgConfig, AddLiquidityConfig
from src.files_manager import read_evm_wallets_from_file


class StakeBase:
    def __init__(self, input_data):
        self.input_data = input_data

    def check_if_float_valid(self, value):
        try:
            value = float(value)
            if value >= 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def check_if_int_valid(self, value):
        try:
            value = int(value)
            if value >= 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def ckeck_min_max(self, min_value, max_value):
        if min_value > max_value:
            return False
        else:
            return True

    def tx_receipt_field_check(self):
        if self.input_data.wait_for_confirmation:
            if not self.input_data.confirmation_timeout_seconds:
                error_msg = 'Wait for confirmation timeout should be specified'
                return error_msg

            if self.check_if_float_valid(self.input_data.confirmation_timeout_seconds) is False:
                error_msg = 'Wait for confirmation timeout is not valid, should be int or float'
                return error_msg

            if self.input_data.confirmation_timeout_seconds <= 0:
                error_msg = 'Wait for confirmation timeout should be greater than 0'
                return error_msg

        return True


class StakeManager(StakeBase):
    def __init__(self, input_data: StakeStgConfig):
        super().__init__(input_data)
        self.input_data = input_data
        self.source_chain = input_data.source_chain

        self.wallets = read_evm_wallets_from_file()

    def check_if_route_eligible(self):
        if len(self.wallets) == 0:
            error_msg = f'No EVM wallets found in evm_wallets.txt'
            return error_msg

        if not self.input_data.source_chain:
            error_msg = 'Source chain is not specified'
            return error_msg

        if self.input_data.stake_all_balance is False:
            if not self.check_if_float_valid(self.input_data.min_amount_to_stake):
                error_msg = 'Min amount to stake is not valid'
                return error_msg

            if not self.check_if_float_valid(self.input_data.max_amount_to_stake):
                error_msg = 'Max amount to stake is not valid'
                return error_msg

            if not self.ckeck_min_max(self.input_data.min_amount_to_stake, self.input_data.max_amount_to_stake):
                error_msg = 'Min amounts should be < than max'
                return error_msg

        if not self.check_if_int_valid(self.input_data.lock_period_months):
            error_msg = 'Lock period is not valid, should in range 1-36'
            return error_msg

        if self.input_data.lock_period_months < 1 or self.input_data.lock_period_months > 36:
            error_msg = 'Lock period is not valid, should in range 1-36'
            return error_msg

        if not self.check_if_float_valid(self.input_data.min_delay_seconds):
            error_msg = 'Min delay seconds is not valid'
            return error_msg

        if not self.check_if_float_valid(self.input_data.max_delay_seconds):
            error_msg = 'Max delay seconds is not valid'
            return error_msg

        if not self.ckeck_min_max(self.input_data.min_delay_seconds, self.input_data.max_delay_seconds):
            error_msg = 'Min amounts should be < than max'
            return error_msg

        if not self.check_if_int_valid(self.input_data.gas_limit):
            error_msg = 'Gas limit is not valid, should be integer'
            return error_msg

        tx_receipt_eligibility = self.tx_receipt_field_check()
        if tx_receipt_eligibility is not True:
            return tx_receipt_eligibility

        return True


class LiquidityManager(StakeBase):
    def __init__(self, input_data: AddLiquidityConfig):
        super().__init__(input_data)
        self.input_data = input_data
        self.source_chain = input_data.source_chain
        self.coin_to_stake = input_data.coin_to_stake

        self.usdt_eligible_chains = ['BSC', 'Polygon', 'Avalanche', 'Arbitrum']
        self.usdc_eligible_chains = ['Polygon', 'Avalanche', 'Arbitrum', 'Fantom', 'Optimism']

        self.wallets = read_evm_wallets_from_file()

    def check_if_route_eligible(self):
        if len(self.wallets) == 0:
            error_msg = f'No EVM wallets found in evm_wallets.txt'
            return error_msg

        if not self.input_data.source_chain:
            error_msg = 'Source chain is not specified'
            return error_msg

        if not self.coin_to_stake:
            error_msg = 'Coin to stake is not specified'
            return error_msg

        if self.coin_to_stake == 'USDT':
            if self.source_chain not in self.usdt_eligible_chains:
                error_msg = f'USDT is not eligible for {self.source_chain}'
                return error_msg

        if self.coin_to_stake == 'USDC':
            if self.source_chain not in self.usdc_eligible_chains:
                error_msg = f'USDC is not eligible for {self.source_chain}'
                return error_msg

        if self.input_data.stake_all_balance is False:
            if not self.check_if_float_valid(self.input_data.min_amount_to_stake):
                error_msg = 'Min amount to stake is not valid'
                return error_msg

            if not self.check_if_float_valid(self.input_data.max_amount_to_stake):
                error_msg = 'Max amount to stake is not valid'
                return error_msg

            if not self.ckeck_min_max(self.input_data.min_amount_to_stake, self.input_data.max_amount_to_stake):
                error_msg = 'Min amount should be < than max'
                return error_msg

        if not self.check_if_int_valid(self.input_data.gas_limit):
            error_msg = 'Gas limit is not valid, should be integer'
            return error_msg

        tx_receipt_eligibility = self.tx_receipt_field_check()
        if tx_receipt_eligibility is not True:
            return tx_receipt_eligibility

        return True

