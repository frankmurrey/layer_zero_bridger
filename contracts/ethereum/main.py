import json

from typing import List

from contracts.ethereum.token_contracts import ethereum_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase
from src.paths import EthereumDir

from web3 import Web3

from src.rpc_manager import RpcValidator

with open(EthereumDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)

with open(EthereumDir.ROUTER_ABI_FILE, "r") as file:
    ETH_ROUTER_ABI = json.load(file)

with open(EthereumDir.APT_ROUTER_ABI_FILE, "r") as file:
    APT_ROUTER_ABI_FILE = json.load(file)

with open(EthereumDir.ENDPOINT_ABI_FILE, "r") as file:
    ENDPOINT_ABI = json.load(file)


class Ethereum(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = ethereum_tokens

        self.chain_id: int = 101
        self.name = "Ethereum"
        self.is_eth_available = True

        web3 = self.web3

        self.eth_router_address = web3.to_checksum_address('0x150f94B44927F078737562f0fcF3C95c01Cc2376')
        self.eth_router_abi = ETH_ROUTER_ABI
        self.eth_router_contract = web3.eth.contract(address=self.eth_router_address, abi=self.eth_router_abi)

        self.router_address = web3.to_checksum_address('0x8731d54E9D02c286767d56ac03e8037C07e01e98')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

        self.aptos_router_address = web3.to_checksum_address('0x50002CdFe7CCb0C41F519c6Eb0653158d11cd907')
        self.aptos_router_abi = APT_ROUTER_ABI_FILE
        self.aptos_router_contract = web3.eth.contract(address=self.aptos_router_address, abi=self.aptos_router_abi)

        self.endpoint_address = web3.to_checksum_address("0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675")
        self.endpoint_abi = ENDPOINT_ABI
        self.endpoint_contract = web3.eth.contract(address=self.endpoint_address, abi=self.endpoint_abi)

    @property
    def web3(self):
        rpc_validator = RpcValidator()
        rpc_list = rpc_validator.validated_rpcs
        web3_base = RpcBase(rpc_list['Ethereum'])
        web3 = Web3(Web3.HTTPProvider(web3_base.get_random_rpc()))
        return web3

