import json

from typing import List

from contracts.optimism.token_contracts import optimism_tokens
from contracts.contracts_base import ContractsBase, Token
from contracts.rpcs import RPC
from src.paths import OptDir

from web3 import Web3

RPC_URL = RPC.Optimism

with open(OptDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(OptDir.ETH_ROUTER_ABI_FILE, "r") as file:
    ETH_ROUTER_ABI = json.load(file)

with open(OptDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(OptDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Optimism(ContractsBase):
    token_contracts: List[Token] = optimism_tokens

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    chain_id: int = 111
    name = "Optimism"

    router_address = web3.to_checksum_address('0xB0D502E938ed5f4df2E681fE6E419ff29631d62b')
    router_abi = ROUTER_ABI
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)

    eth_router_address = web3.to_checksum_address('0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b')
    eth_router_abi = ETH_ROUTER_ABI
    eth_router_contract = web3.eth.contract(address=eth_router_address, abi=eth_router_abi)

    aptos_router_address = web3.to_checksum_address('0x86Bb63148d17d445Ed5398ef26Aa05Bf76dD5b59')
    aptos_router_abi = APT_ROUTER_ABI_FILE
    aptos_router_contract = web3.eth.contract(address=aptos_router_address, abi=aptos_router_abi)

    endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
    endpoint_abi = ENDPOINT_ABI
    endpoint_contract = web3.eth.contract(address=endpoint_address, abi=endpoint_abi)
