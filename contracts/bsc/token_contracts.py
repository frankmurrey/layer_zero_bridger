import json

from src.paths import BscDir
from contracts.contracts_base import Token

with open(BscDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)


bsc_tokens = [
    Token(name="USDT", abi=USDT_ABI, address="0x55d398326f99059fF775485246999027B3197955", pool_id=2)
]

