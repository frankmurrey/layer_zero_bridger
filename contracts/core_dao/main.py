from typing import List

from contracts.core_dao.token_contracts import core_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import CoreDaoDir

from web3 import Web3

from loguru import logger

from src.rpc_manager import RpcValidator


class CoreDao(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = core_tokens

        self.chain_id: int = 153
        self.name = "CoreDao"
        self.is_eth_available = False

        web3 = self.web3

    @property
    def web3(self):
        rpc_validator = RpcValidator()
        rpc_list = rpc_validator.validated_rpcs
        rpc_chain_list = rpc_list[self.name]
        if len(rpc_chain_list) == 0:
            logger.error(f"Please provide at least one valid {self.name} RPC → contracts/rpcs.json")
            exit(1)

        web3_base = RpcBase(rpc_chain_list)
        random_rpc = web3_base.get_random_rpc()
        web3 = Web3(Web3.HTTPProvider(random_rpc))
        return web3
