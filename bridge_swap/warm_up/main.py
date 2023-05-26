import time
import random
import datetime

from typing import List, Union

from bridge_swap.warm_up import WarmUpManager, WalletManager
from bridge_swap.warm_up.router import WarmUpRouter

from bridge_swap.stargate.token_bridge import TokenBridgeManual
from bridge_swap.stargate.eth_bridge import EthBridgeManual

from src.schemas.config import WarmUpConfigSchema, ConfigSchema
from src.schemas.warmup_wallet import WarmUpWalletSchema
from src.config import get_warmup_config, get_config_from_dict, print_config
from src.bridge_manager import BridgeManager
from src.files_manager import read_evm_wallets_from_file, get_all_wallets_logs_data, save_summary_log_file

from loguru import logger


def initialize_all_wallets():
    all_wallets = read_evm_wallets_from_file()
    new_wallets_amount, old_wallets_amount = 0, 0
    for wallet in all_wallets:
        wallet_manager = WalletManager(private_key=wallet)
        status: bool = wallet_manager.initiate_wallet()
        if status is False:
            new_wallets_amount += 1
        else:
            old_wallets_amount += 1

    save_summary_log_file()
    logger.info(f'Created ({new_wallets_amount}) new log files,'
                f' already exists ({old_wallets_amount}) wallet log files\n')


def warm_up(config=None):
    if config is None:
        warmup_config: WarmUpConfigSchema = get_warmup_config()
    else:
        warmup_config: WarmUpConfigSchema = config

    wallet_handler = WalletHandler(config=warmup_config)
    print_config(config=warmup_config,
                 delay_seconds=10)

    while True:
        wallet_to_warm_up = wallet_handler.get_wallet(random_state=warmup_config.shuffle_wallets_order)
        if wallet_to_warm_up is None:
            logger.warning('Bridge process ended, or no more valid wallets to warm up')
            break

        warmup = WarmUp(private_key=wallet_to_warm_up, config=warmup_config)
        warmup.make_bridge()

        time_delay = random.randint(warmup_config.min_delay_seconds, warmup_config.max_delay_seconds)
        logger.info(f'Waiting ({time_delay}) seconds to start next wallet\n')
        time.sleep(time_delay)


class WalletHandler:
    def __init__(self, config: WarmUpConfigSchema):
        self.config: WarmUpConfigSchema = config
        self.all_wallet_logs: List[dict] = get_all_wallets_logs_data()
        self.all_wallet_private_keys: List[str] = read_evm_wallets_from_file()

    def blur_private_key(self, private_key: str) -> str:
        length = len(private_key)
        start_index = length // 3
        end_index = length - start_index
        blurred_private_key = private_key[:start_index] + '*' * (end_index - start_index) + private_key[end_index:]
        return blurred_private_key

    def get_all_wallet_private_keys(self) -> List[str]:
        all_wallet_private_keys = []
        for wallet_log in self.all_wallet_logs:
            if wallet_log['private_key'] is not None:
                all_wallet_private_keys.append(wallet_log['private_key'])

        return all_wallet_private_keys

    def get_wallet(self, random_state: bool = False):
        try:
            if random_state:
                random_wallet_pr_key = random.choice(self.all_wallet_private_keys)
                self.all_wallet_private_keys.remove(random_wallet_pr_key)
                # wallet_bridge_needed = self.check_wallet_bridge_needed(random_wallet_pr_key)

                logger.info(f'[{self.blur_private_key(private_key=random_wallet_pr_key)}] '
                            f'- got wallet private key for bridge,'
                            f' random state: {random_state}')
                return random_wallet_pr_key
            else:
                if len(self.all_wallet_private_keys) == 0:
                    return None

                wallet_private_key = self.all_wallet_private_keys.pop(0)
                # wallet_bridge_needed = self.check_wallet_bridge_needed(wallet_private_key)

                logger.info(f'[{self.blur_private_key(private_key=wallet_private_key)}]'
                            f' - got wallet private key for bridge,'
                            f' random state: {random_state}')
                return wallet_private_key

        except IndexError as e:
            logger.error(f'Error while getting wallet: {e}')
            return None

    def check_wallet_bridge_needed(self, private_key) -> bool:
        wallet_manager: WalletManager = WalletManager(private_key=private_key)
        wallet_data: WarmUpWalletSchema = wallet_manager.get_wallet_data()

        if wallet_data is None:
            logger.error(f'Error while getting wallet data')
            return False

        if wallet_data.last_bridge_status is None:
            return True

        if time.time() - wallet_data.last_bridge_time <= self.config.max_delay_seconds:
            if wallet_data.last_bridge_status is True:
                return False
            else:
                return True
        return True


class WarmUp(WarmUpManager):
    def __init__(self, config: WarmUpConfigSchema, private_key: str):
        super().__init__(config=config)
        self.config = config
        self.private_key = private_key
        self.wallet_address = self.get_wallet_address(private_key=self.private_key)

        self.chain_balances: dict = self.fetch_wallet_chain_balances(wallet_address=self.wallet_address)
        self.route_checker: WarmUpRouter = WarmUpRouter(config=config,
                                                        chain_balances=self.chain_balances)

    def build_bridge_config(self):

        if self.config.coin_to_transfer.lower() == 'stable_coins':
            swap_route = self.route_checker.get_swap_route_stables()
            if swap_route is None:
                logger.error(f'[{self.wallet_address}] - Error while getting stable swap route, check wallet balance')
                return None

        elif self.config.coin_to_transfer.lower() == 'ethereum':
            swap_route = self.route_checker.get_swap_route_eth()
            if swap_route is None:
                logger.error(f'[{self.wallet_address}] - Error while getting eth swap route, check wallet balance')
                return None

        else:
            logger.error(f'[{self.wallet_address}] - Coin to transfer is not supported')
            return None

        if swap_route is None:
            logger.error(f'[{self.wallet_address}] - Error while getting swap route')
            return None

        token_amount_to_transfer = self.get_random_amount(min_amount=self.config.min_amount_to_transfer,
                                                          max_amount=self.config.max_amount_to_transfer)
        source_chain = swap_route['source_chain']
        target_chain = swap_route['target_chain']
        coin_to_transfer = swap_route['coin']
        min_bridge_amount = token_amount_to_transfer
        max_bridge_amount = token_amount_to_transfer
        gas_limit = self.config.max_gas_limit
        slippage = self.config.slippage
        test_mode = self.config.test_mode

        config_dict = {
            'source_chain': source_chain,
            'target_chain': target_chain,
            'min_bridge_amount': min_bridge_amount,
            'max_bridge_amount': max_bridge_amount,
            'coin_to_transfer': coin_to_transfer,
            'gas_limit': gas_limit,
            'slippage': slippage,
            'test_mode': test_mode
        }

        config_manual_data: ConfigSchema = get_config_from_dict(config_dict=config_dict)
        if config_manual_data is None:
            logger.error(f'[{self.wallet_address}] - Error while getting config manual data')
            return None

        return config_manual_data

    def make_bridge(self):
        wallet_manager: WalletManager = WalletManager(private_key=self.private_key)

        config_data = self.build_bridge_config()
        if config_data is None:
            return None
        bridge_manager = BridgeManager(input_data=config_data)
        route_eligibility: Union[bool, str] = bridge_manager.check_if_route_eligible()
        if route_eligibility is not True:
            logger.error(f'[{self.wallet_address}] - {route_eligibility}')
            return None

        if self.config.coin_to_transfer.lower() == 'stable_coins':
            token_bridge = TokenBridgeManual(config=config_data)
            required_allowance = config_data.max_bridge_amount
            wallet_address = token_bridge.get_wallet_address(private_key=self.private_key)
            allowed_amount_to_bridge = token_bridge.check_allowance(wallet_address=wallet_address,
                                                                    token_contract=token_bridge.token_contract,
                                                                    spender=token_bridge.source_chain.router_address)
            if allowed_amount_to_bridge < required_allowance:
                logger.warning(
                    f"[{wallet_address}] - Not enough allowance for {token_bridge.token_obj.name},"
                    f" approving {token_bridge.token_obj.name} to bridge")
                make_approve = token_bridge.approve_token_transfer(private_key=self.private_key,
                                                                   approve_amount=required_allowance,
                                                                   wallet_address=wallet_address)

                if make_approve is not True:
                    return None

            tx_hash = token_bridge.transfer(private_key=self.private_key)
            if tx_hash:
                wallet_data: dict = {
                    'last_bridge_status': True,
                    'last_bridge_time': time.time(),
                    'last_bridge_tx_hash': tx_hash,
                    'last_bridge_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                wallet_manager.update_wallet_log_file(data=wallet_data)

        elif self.config.coin_to_transfer.lower() == 'ethereum':
            eth_bridge = EthBridgeManual(config=config_data)
            tx_hash = eth_bridge.transfer(private_key=self.private_key)
            if tx_hash:
                wallet_data: dict = {
                    'last_bridge_status': True,
                    'last_bridge_time': time.time(),
                    'last_bridge_tx_hash': tx_hash,
                    'last_bridge_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                wallet_manager.update_wallet_log_file(data=wallet_data)


