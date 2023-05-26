import json

from typing import List

from contracts.core_dao.token_contracts import core_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import CoreDaoDir

from web3 import Web3

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
        web3_base = RpcBase(rpc_list['CoreDao'])
        web3 = Web3(Web3.HTTPProvider(web3_base.get_random_rpc()))
        return web3
