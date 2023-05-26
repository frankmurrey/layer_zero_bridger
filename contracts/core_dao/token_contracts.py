import json

from src.paths import CoreDaoDir
from contracts.contracts_base import Token

with open(CoreDaoDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)


core_tokens = [
    Token(name="USDT", abi=USDT_ABI, address="0x900101d06A7426441Ae63e9AB3B9b0F63Be145F1", pool_id=2)
]

