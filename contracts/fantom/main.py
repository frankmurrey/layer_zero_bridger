import json

from typing import List

from contracts.fantom.token_contracts import fantom_tokens
from contracts.contracts_base import ContractsBase, Token, RpcBase

from src.paths import FantomDir

from web3 import Web3
from loguru import logger

from src.rpc_manager import RpcValidator

with open(FantomDir.ROUTER_ABI_FILE, "r") as file:
    ROUTER_ABI = json.load(file)


class Fantom(ContractsBase):
    def __init__(self):
        super().__init__()
        self.token_contracts: List[Token] = fantom_tokens

        self.chain_id: int = 112
        self.name = "Fantom"
        self.is_eth_available = False

        web3 = self.web3

        self.router_address = web3.to_checksum_address('0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6')
        self.router_abi = ROUTER_ABI
        self.router_contract = web3.eth.contract(address=self.router_address, abi=self.router_abi)

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

