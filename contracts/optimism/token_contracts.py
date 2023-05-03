import json

from src.paths import OptDir
from contracts.contracts_base import Token

with open(OptDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)

with open(OptDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)


optimism_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0x7f5c764cbc14f9669b88837ca1490cca17c31607", pool_id=1),
]

