import json

from src.paths import PolygonDir
from contracts.contracts_base import Token

with open(PolygonDir.USDT_ABI_FILE, "r") as file:
    USDT_ABI = json.load(file)

with open(PolygonDir.USDC_ABI_FILE, "r") as file:
    USDC_ABI = json.load(file)

with open(PolygonDir.STG_ABI_FILE, "r") as file:
    STG_ABI = json.load(file)


polygon_tokens = [
    Token(name="USDC", abi=USDC_ABI, address="0x2791bca1f2de4661ed88a30c99a7a9449aa84174", pool_id=1),
    Token(name="USDT", abi=USDT_ABI, address="0xc2132D05D31c914a87C6611C10748AEb04B58e8F", pool_id=2),
    Token(name="STG", abi=STG_ABI, address="0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590", pool_id=None)
]
