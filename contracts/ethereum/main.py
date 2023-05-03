import json

from typing import List

from contracts.ethereum.token_contracts import ethereum_tokens
from contracts.contracts_base import ContractsBase, Token
from contracts.rpcs import RPC
from src.paths import EthereumDir

from web3 import Web3

RPC_URL = RPC.Ethereum

with open(EthereumDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(EthereumDir.ROUTER_ABI_FILE, "r") as file:
    ETH_ROUTER_ABI = json.load(file)

with open(EthereumDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(EthereumDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Ethereum(ContractsBase):
    token_contracts: List[Token] = ethereum_tokens

    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    chain_id: int = 101
    name = "Ethereum"

    eth_router_address = web3.to_checksum_address('0x150f94B44927F078737562f0fcF3C95c01Cc2376')
    eth_router_abi = ETH_ROUTER_ABI
    eth_router_contract = web3.eth.contract(address=eth_router_address, abi=eth_router_abi)

    router_address = web3.to_checksum_address('0x8731d54E9D02c286767d56ac03e8037C07e01e98')
    router_abi = ROUTER_ABI
    router_contract = web3.eth.contract(address=router_address, abi=router_abi)

    aptos_router_address = web3.to_checksum_address('0x50002CdFe7CCb0C41F519c6Eb0653158d11cd907')
    aptos_router_abi = APT_ROUTER_ABI_FILE
    aptos_router_contract = web3.eth.contract(address=aptos_router_address, abi=aptos_router_abi)

    endpoint_address = web3.to_checksum_address("0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675")
    endpoint_abi = ENDPOINT_ABI
    endpoint_contract = web3.eth.contract(address=endpoint_address, abi=endpoint_abi)
