import json
import random

from typing import List

from contracts.avalanche.token_contracts import avalanche_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import AvalancheDir

from web3 import Web3

from src.rpc_manager import RpcValidator

with open(AvalancheDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(AvalancheDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(AvalancheDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Avalanche(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = avalanche_tokens

        self.chain_id: int = 106
        self.name = "Avalanche"
        self.is_eth_available = False

        web3 = self.web3

        self.router_address = web3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

        self.aptos_router_address = web3.to_checksum_address('0xA5972EeE0C9B5bBb89a5B16D1d65f94c9EF25166')
        self.aptos_router_abi = APT_ROUTER_ABI_FILE
        self.aptos_router_contract = web3.eth.contract(address=self.aptos_router_address,
                                                       abi=self.aptos_router_abi)

        self.endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
        self.endpoint_abi = ENDPOINT_ABI
        self.endpoint_contract = web3.eth.contract(address=self.endpoint_address, abi=self.endpoint_abi)

    @property
    def web3(self):
        rpc_validator = RpcValidator()
        rpc_list = rpc_validator.validated_rpcs
        web3_base = RpcBase(rpc_list['Avalanche'])
        web3 = Web3(Web3.HTTPProvider(web3_base.get_random_rpc()))
        return web3
