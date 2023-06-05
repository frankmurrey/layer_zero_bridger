import json

from src.paths import EthereumDir
from contracts.contracts_base import Token

with open(EthereumDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)

with open(EthereumDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)

with open(EthereumDir.STG_ABI_FILE, "r") as file:
    STG_ABI = json.load(file)


ethereum_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", pool_id=1),
    Token(name="USDT", abi=USDT_ABI, address="0xdac17f958d2ee523a2206206994597c13d831ec7", pool_id=2),
    Token(name="STG", abi=STG_ABI, address="0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6", pool_id=None)
]
