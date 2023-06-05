import json

from typing import List

from loguru import logger

from contracts.arbitrum.token_contracts import arbitrum_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import ArbDir

from web3 import Web3

from src.rpc_manager import RpcValidator

with open(ArbDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(ArbDir.ETH_ROUTER_ABI_FILE, "r") as file:
    ETH_ROUTER_ABI = json.load(file)

with open(ArbDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(ArbDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)

with open(ArbDir.VOTING_ABI_FILE, "r") as file:
    VOTING_ABI = json.load(file)


class Arbitrum(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = arbitrum_tokens

        self.chain_id: int = 110
        self.name = "Arbitrum"
        self.is_eth_available = True

        web3 = self.web3

        self.eth_router_address = web3.to_checksum_address('0xbf22f0f184bccbea268df387a49ff5238dd23e40')
        self.eth_router_abi = ETH_ROUTER_ABI
        self.eth_router_contract = web3.eth.contract(address=self.eth_router_address, abi=self.eth_router_abi)

        self.router_address = web3.to_checksum_address('0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

        self.aptos_router_address = web3.to_checksum_address('0x1BAcC2205312534375c8d1801C27D28370656cFf')
        self.aptos_router_abi = APT_ROUTER_ABI_FILE
        self.aptos_router_contract = web3.eth.contract(address=self.aptos_router_address, abi=self.aptos_router_abi)

        self.endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
        self.endpoint_abi = ENDPOINT_ABI
        self.endpoint_contract = web3.eth.contract(address=self.endpoint_address, abi=self.endpoint_abi)

        self.voting_address = web3.to_checksum_address("0xfBd849E6007f9BC3CC2D6Eb159c045B8dc660268")
        self.voting_abi = VOTING_ABI
        self.voting_contract = web3.eth.contract(address=self.voting_address, abi=self.voting_abi)

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


