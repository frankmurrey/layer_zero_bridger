import json

from src.paths import FantomDir
from contracts.contracts_base import Token

with open(FantomDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)

with open(FantomDir.STG_ABI_FILE, "r") as file:
    STG_ABI = json.load(file)


fantom_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0x04068DA6C83AFCFA0e13ba15A6696662335D5B75", pool_id=1),
    Token(name="STG", abi=STG_ABI, address="0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590", pool_id=None)
]
