import json

from typing import List

from contracts.arbitrum.token_contracts import arbitrum_tokens
from contracts.contracts_base import ContractsBase, Token
from contracts.rpcs import RPC
from src.paths import ArbDir

from web3 import Web3

RPC_URL = RPC.Arbitrum

with open(ArbDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(ArbDir.ETH_ROUTER_ABI_FILE, "r") as file:
    ETH_ROUTER_ABI = json.load(file)

with open(ArbDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(ArbDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Arbitrum(ContractsBase):
    token_contracts: List[Token] = arbitrum_tokens

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    chain_id: int = 110
    name = "Arbitrum"

    eth_router_address = web3.to_checksum_address('0xbf22f0f184bccbea268df387a49ff5238dd23e40')
    eth_router_abi = ETH_ROUTER_ABI
    eth_router_contract = web3.eth.contract(address=eth_router_address, abi=eth_router_abi)

    router_address = web3.to_checksum_address('0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614')
    router_abi = ROUTER_ABI
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)

    aptos_router_address = web3.to_checksum_address('0x1BAcC2205312534375c8d1801C27D28370656cFf')
    aptos_router_abi = APT_ROUTER_ABI_FILE
    aptos_router_contract = web3.eth.contract(address=aptos_router_address, abi=aptos_router_abi)

    endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
    endpoint_abi = ENDPOINT_ABI
    endpoint_contract = web3.eth.contract(address=endpoint_address, abi=endpoint_abi)
