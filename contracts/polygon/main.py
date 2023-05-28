import json

from typing import List

from contracts.polygon.token_contracts import polygon_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import PolygonDir
from src.rpc_manager import RpcValidator

from web3 import Web3
from loguru import logger

with open(PolygonDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(PolygonDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(PolygonDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Polygon(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = polygon_tokens

        self.chain_id: int = 109
        self.name = "Polygon"
        self.is_eth_available = False

        web3 = self.web3

        self.router_address = web3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

        self.aptos_router_address = web3.to_checksum_address('0x488863D609F3A673875a914fBeE7508a1DE45eC6')
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
