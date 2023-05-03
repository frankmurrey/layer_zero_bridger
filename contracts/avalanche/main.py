import json

from typing import List

from contracts.avalanche.token_contracts import avalanche_tokens
from contracts.contracts_base import ContractsBase, Token
from contracts.rpcs import RPC
from src.paths import AvalancheDir

from web3 import Web3

RPC_URL = RPC.Avalanche

with open(AvalancheDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(AvalancheDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(AvalancheDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Avalanche(ContractsBase):
    token_contracts: List[Token] = avalanche_tokens

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    chain_id: int = 106
    name = "Avalanche"

    router_address = web3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
    router_abi = ROUTER_ABI
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)

    aptos_router_address = web3.to_checksum_address('0xA5972EeE0C9B5bBb89a5B16D1d65f94c9EF25166')
    aptos_router_abi = APT_ROUTER_ABI_FILE
    aptos_router_contract = web3.eth.contract(address=aptos_router_address, abi=aptos_router_abi)

    endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
    endpoint_abi = ENDPOINT_ABI
    endpoint_contract = web3.eth.contract(address=endpoint_address, abi=endpoint_abi)
