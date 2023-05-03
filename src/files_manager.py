import yaml

from src.paths import CONFIG_FILE, WALLETS_FILE, APTOS_WALLETS_FILE
from loguru import logger


def read_evm_wallets_from_file():
    try:
        with open(WALLETS_FILE, "r") as file:
            wallets_from_txt = file.read().splitlines()
            if wallets_from_txt is None:
                return []
            return [x for x in wallets_from_txt if x and x.strip() and len(x) == 66]
    except FileNotFoundError:
        logger.error("Wallets file not found")
        return []


def read_aptos_wallets_from_file():
    try:
        with open(APTOS_WALLETS_FILE, "r") as file:
            wallets_from_txt = file.read().splitlines()
            if wallets_from_txt is None:
                print("No wallets found")
                return []
            return [x for x in wallets_from_txt if x and x.strip() and len(x) == 66]
    except FileNotFoundError:
        logger.error("Wallets file not found")
        return []


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=True)


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("Config file not found")