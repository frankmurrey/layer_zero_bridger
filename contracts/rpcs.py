import json

from src.paths import RPCS_FILE
from src.templates import create_rpcs_file

try:
    with open(RPCS_FILE, "r") as f:
        RPC = json.load(f)
except FileNotFoundError:
    create_rpcs_file()
    with open(RPCS_FILE, "r") as f:
        RPC = json.load(f)


# Please change rpc URLS there →: contracts\rpcs.json
# Please change rpc URLS there →: contracts\rpcs.json
# Please change rpc URLS there →: contracts\rpcs.json

