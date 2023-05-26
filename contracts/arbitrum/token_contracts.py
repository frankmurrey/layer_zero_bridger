import json

from src.paths import ArbDir
from contracts.contracts_base import Token

with open(ArbDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)

with open(ArbDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)

arbitrum_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0xff970a61a04b1ca14834a43f5de4533ebddb5cc8", pool_id=1),
    Token(name="USDT", abi=USDT_ABI, address="0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", pool_id=2)
]

