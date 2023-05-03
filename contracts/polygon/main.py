import json

from typing import List

from contracts.polygon.token_contracts import polygon_tokens
from contracts.contracts_base import ContractsBase, Token
from contracts.rpcs import RPC
from src.paths import PolygonDir

from web3 import Web3

RPC_URL = RPC.Polygon

with open(PolygonDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(PolygonDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(PolygonDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Polygon(ContractsBase):
    token_contracts: List[Token] = polygon_tokens

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    chain_id: int = 109
    name = "Polygon"

    router_address = web3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
    router_abi = ROUTER_ABI
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)

    aptos_router_address = web3.to_checksum_address('0x488863D609F3A673875a914fBeE7508a1DE45eC6')
    aptos_router_abi = APT_ROUTER_ABI_FILE
    aptos_router_contract = web3.eth.contract(address=aptos_router_address, abi=aptos_router_abi)

    endpoint_address = web3.to_checksum_address("0x3c2269811836af69497E5F486A85D7316753cf62")
    endpoint_abi = ENDPOINT_ABI
    endpoint_contract = web3.eth.contract(address=endpoint_address, abi=endpoint_abi)

