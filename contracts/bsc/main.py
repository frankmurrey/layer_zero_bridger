import json

from typing import List

from contracts.bsc.token_contracts import bsc_tokens
from contracts.contracts_base import ContractsBase, Token
from contracts.rpcs import RPC
from src.paths import BscDir

from web3 import Web3

RPC_URL = RPC.BSC

with open(BscDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(BscDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(BscDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Bsc(ContractsBase):
    token_contracts: List[Token] = bsc_tokens

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    chain_id: int = 102
    name = "BSC"

    router_address = web3.to_checksum_address('0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8')
    router_abi = ROUTER_ABI
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)

    aptos_router_address = web3.to_checksum_address('0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B')
    aptos_router_abi = APT_ROUTER_ABI_FILE
    aptos_router_contract = web3.eth.contract(address=aptos_router_address, abi=aptos_router_abi)

    endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
    endpoint_abi = ENDPOINT_ABI
    endpoint_contract = web3.eth.contract(address=endpoint_address, abi=endpoint_abi)
