import json

from src.paths import ArbDir
from contracts.contracts_base import Token

with open(ArbDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)

with open(ArbDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)


arbitrum_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0xff970a61a04b1ca14834a43f5de4533ebddb5cc8", pool_id=1),
    Token(name="USDT", abi=USDT_ABI, address="0xdAC17F958D2ee523a2206206994597C13D831ec7", pool_id=2)
]

