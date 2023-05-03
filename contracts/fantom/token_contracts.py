import json

from src.paths import FantomDir
from contracts.contracts_base import Token

with open(FantomDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)


fantom_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0x04068DA6C83AFCFA0e13ba15A6696662335D5B75", pool_id=1),
]

