import random

from src.schemas.config import WarmUpConfigSchema
from src.config import get_warmup_config

from loguru import logger


class WarmUpRouter:
    def __init__(self, config: WarmUpConfigSchema, chain_balances: dict):
        self.config = config
        self.chain_options = config.chain_options
        self.chain_balances = chain_balances
        self.stable_coin_names = ['USDC', 'USDT']
        self.eth_coin_name = 'Ethereum'

    def get_source_chain_stables(self):
        try:
            available_chains = {}
            for chain in self.chain_balances.keys():
                if chain not in self.chain_options:
                    continue
                available_stables = []
                for stable_coin in self.stable_coin_names:
                    if stable_coin not in self.chain_balances[chain].keys():
                        continue
                    if self.chain_balances[chain][stable_coin] >= self.config.min_amount_to_transfer:
                        available_stables.append(stable_coin)
                        available_chains[chain] = available_stables

            random_key = random.choice(list(available_chains.keys()))
            random_chain = {random_key: available_chains[random_key]}

            return random_chain
        except Exception as ex:
            logger.error(f'Error while getting source chain for stables bridge: {ex}')
            return None

    def get_target_chain_stables(self, source_chain_name):
        try:
            available_chains = []
            for chain in self.chain_options:
                if chain != source_chain_name:
                    available_chains.append(chain)

            random_chain = random.choice(available_chains)
            return random_chain
        except IndexError:
            logger.error('No target chain available, pleas check your config file or wallet balances')
            return None

    def get_swap_route_stables(self):
        source_chain_stables = self.get_source_chain_stables()
        source_chain_name = list(source_chain_stables.keys())[0]
        target_chain_name = self.get_target_chain_stables(source_chain_name=source_chain_name)
        random_stable_coin = random.choice(source_chain_stables[source_chain_name])
        if target_chain_name is None or source_chain_name is None or random_stable_coin is None:
            return None

        return {'source_chain': source_chain_name, 'target_chain': target_chain_name, 'coin': random_stable_coin}

    def get_source_chain_eth(self):
        try:
            available_chains = {}
            for chain in self.chain_balances.keys():
                if chain not in self.chain_options:
                    continue
                if self.eth_coin_name in self.chain_balances[chain].keys():
                    if self.chain_balances[chain][self.eth_coin_name] >= self.config.min_amount_to_transfer:
                        available_chains[chain] = self.eth_coin_name
            random_key = random.choice(list(available_chains.keys()))
            random_chain = {random_key: available_chains[random_key]}

            return random_chain
        except Exception as ex:
            logger.error(f'Error while getting source chain for eth bridge: {ex},'
                         f' check your config file or wallet balances')
            return None

    def get_target_chain_eth(self, source_chain_name):
        try:
            available_chains = []
            for chain in self.chain_options:
                if chain == source_chain_name:
                    continue
                if chain not in self.chain_balances.keys():
                    continue
                if self.eth_coin_name not in self.chain_balances[chain].keys():
                    continue

                available_chains.append(chain)

            random_chain = random.choice(available_chains)
            return random_chain
        except Exception as ex:
            logger.error(f'Error: {ex}. No target chain available, pleas check your config file or wallet balances')
            return None

    def get_swap_route_eth(self):
        source_chain_eth = self.get_source_chain_eth()
        source_chain_name = list(source_chain_eth.keys())[0]
        target_chain_name = self.get_target_chain_eth(source_chain_name=source_chain_name)
        if target_chain_name is None or source_chain_name is None:
            return None

        return {'source_chain': source_chain_name, 'target_chain': target_chain_name, 'coin': self.eth_coin_name}


if __name__ == '__main__':
    config = get_warmup_config()
    router = WarmUpRouter(config=config,
                          chain_balances={'Arbitrum': {'Ethereum': 0.09743419575630895, 'USDC': 935.579303, 'USDT': 100.817915}, 'Optimism': {'Ethereum': 0.16087755505926946, 'USDC': 1084.16429}, 'Ethereum': {'Ethereum': 0.23172092674477782}, 'Avalanche': {'USDC': 1084.16429}})
    print(router.get_swap_route_stables())

