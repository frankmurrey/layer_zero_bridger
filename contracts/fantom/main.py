import json

from typing import List

from contracts.fantom.token_contracts import fantom_tokens
from contracts.contracts_base import ContractsBase, Token
from contracts.rpcs import RPC
from src.paths import FantomDir

from web3 import Web3

RPC_URL = RPC.Fantom

with open(FantomDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)


class Fantom(ContractsBase):
    token_contracts: List[Token] = fantom_tokens

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    chain_id: int = 112
    name = "Fantom"

    router_address = web3.to_checksum_address('0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6')
    router_abi = ROUTER_ABI
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)

