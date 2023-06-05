import json

from typing import List

from contracts.core_dao.token_contracts import core_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import CoreDaoDir

from web3 import Web3

from loguru import logger

from src.rpc_manager import RpcValidator

with open(CoreDaoDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(CoreDaoDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class CoreDao(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = core_tokens

        self.chain_id: int = 153
        self.name = "CoreDao"
        self.is_eth_available = False

        web3 = self.web3

        self.router_address = web3.to_checksum_address('0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

        self.endpoint_address = web3.to_checksum_address("0x9740FF91F1985D8d2B71494aE1A2f723bb3Ed9E4")
        self.endpoint_abi = ENDPOINT_ABI
        self.endpoint_contract = web3.eth.contract(address=self.endpoint_address, abi=self.endpoint_abi)

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
