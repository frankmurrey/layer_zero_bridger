from bridge_swap.warm_up import WarmUpManager, WalletManager
from src.schemas.config import WarmUpConfigSchema
from bridge_swap.warm_up.router import WarmUpRouter

from src.config import get_warmup_config


class WarmUp(WarmUpManager):
    def __init__(self, config: WarmUpConfigSchema, private_key: str):
        super().__init__(config=config)
        self.config = config
        self.private_key = private_key
        self.wallet_address = self.get_wallet_address(private_key=self.private_key)

        self.chain_balances: dict = self.fetch_wallet_chain_balances(wallet_address=self.wallet_address)

        self.wallet_manager: WalletManager = WalletManager(private_key=self.private_key)
        self.route_checker: WarmUpRouter = WarmUpRouter(config=config,
                                                        chain_balances=self.chain_balances)

    def pick_stable_coin(self):
        pass


if __name__ == '__main__':
    config_data = get_warmup_config()
    wup = WarmUp(config=config_data, private_key='0x6dc222442afb2862dafb6bbb316d930c1428dee21ccb458fba47e60033d64d20')
    # print(wup.fetch_wallet_chain_balances(wallet_address='0x2e57b4f9e56E3C98a25bBB966CEC90a99F8d09c1'))
