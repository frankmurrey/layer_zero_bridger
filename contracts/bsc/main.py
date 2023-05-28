import json

from typing import List

from contracts.bsc.token_contracts import bsc_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import BscDir

from web3 import Web3

from src.rpc_manager import RpcValidator

from loguru import logger


with open(BscDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(BscDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(BscDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)

with open(BscDir.CORE_DAO_ROUTER_ABI_FILE, "r") as file:
    CORE_DAO_ROUTER_ABI = json.load(file)


class BSC(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = bsc_tokens

        self.chain_id: int = 102
        self.name = "BSC"
        self.is_eth_available = False

        web3 = self.web3

        self.router_address = web3.to_checksum_address('0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

        self.aptos_router_address = web3.to_checksum_address('0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B')
        self.aptos_router_abi = APT_ROUTER_ABI_FILE
        self.aptos_router_contract = web3.eth.contract(address=self.aptos_router_address, abi=self.aptos_router_abi)

        self.endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
        self.endpoint_abi = ENDPOINT_ABI
        self.endpoint_contract = web3.eth.contract(address=self.endpoint_address, abi=self.endpoint_abi)

        self.core_dao_router_address = web3.to_checksum_address("0x52e75d318cfb31f9a2edfa2dfee26b161255b233")
        self.core_dao_router_abi = CORE_DAO_ROUTER_ABI
        self.core_dao_router_contract = web3.eth.contract(address=self.core_dao_router_address, abi=self.core_dao_router_abi)

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
