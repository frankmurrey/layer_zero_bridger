import json

from src.paths import AvalancheDir
from contracts.contracts_base import Token

with open(AvalancheDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)

with open(AvalancheDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)


avalanche_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", pool_id=1),
    Token(name="USDT", abi=USDT_ABI, address="0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7", pool_id=2)
]

