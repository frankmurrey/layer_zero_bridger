import json

from typing import List

from contracts.optimism.token_contracts import optimism_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import OptDir

from web3 import Web3
from loguru import logger

from src.rpc_manager import RpcValidator

with open(OptDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(OptDir.ETH_ROUTER_ABI_FILE, "r") as file:
    ETH_ROUTER_ABI = json.load(file)

with open(OptDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(OptDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Optimism(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = optimism_tokens

        self.chain_id: int = 111
        self.name = "Optimism"
        self.is_eth_available = True

        web3 = self.web3

        self.router_address = web3.to_checksum_address('0xB0D502E938ed5f4df2E681fE6E419ff29631d62b')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

        self.eth_router_address = web3.to_checksum_address('0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b')
        self.eth_router_abi = ETH_ROUTER_ABI
        self.eth_router_contract = web3.eth.contract(address=self.eth_router_address, abi=self.eth_router_abi)

        self.aptos_router_address = web3.to_checksum_address('0x86Bb63148d17d445Ed5398ef26Aa05Bf76dD5b59')
        self.aptos_router_abi = APT_ROUTER_ABI_FILE
        self.aptos_router_contract = web3.eth.contract(address=self.aptos_router_address, abi=self.aptos_router_abi)

        self.endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
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