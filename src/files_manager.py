import os
import json

import yaml

from src.paths import CONFIG_FILE, WALLETS_FILE, APTOS_WALLETS_FILE, WARM_UP_CONFIG_FILE, WALLET_LOGS_DIR, MAIN_DIR
from src.paths import LIQUIDITY_CONFIG_FILE, STAKE_STG_CONFIG_FILE
from loguru import logger


def create_yaml_file(file_path, data):
    with open(file_path, "w") as f:
        yaml.dump(data, f)
        logger.info(f"Created new file - {file_path}\n")


def create_json_file(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        logger.info(f"Created new file - {file_path}\n")


def check_if_file_exists(file_path):
    if os.path.isfile(file_path):
        return True
    else:
        return False


def create_empty_evm_wallets_file():
    with open(WALLETS_FILE, "w") as file:
        file.write("")
        logger.info("Created evm wallets file")


def read_evm_wallets_from_file():
    try:
        with open(WALLETS_FILE, "r") as file:
            wallets_from_txt = file.read().splitlines()
            if wallets_from_txt is None:
                return []
            return [x for x in wallets_from_txt if x and x.strip() and len(x) == 66]
    except FileNotFoundError:
        logger.error("Wallets file not found")
        create_empty_evm_wallets_file()
        return []


def create_empty_aptos_wallets_file():
    with open(APTOS_WALLETS_FILE, "w") as file:
        file.write("")
        logger.info("Created aptos addresses file")


def read_aptos_wallets_from_file():
    try:
        with open(APTOS_WALLETS_FILE, "r") as file:
            wallets_from_txt = file.read().splitlines()
            if wallets_from_txt is None:
                return []
            return [x for x in wallets_from_txt if x and x.strip() and len(x) == 66]
    except FileNotFoundError:
        logger.error("Aptos addresses file not found, ignore this message if you don't use Aptos Bridge")
        create_empty_aptos_wallets_file()
        return []


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=True)


def save_warmup_config(config):
    with open(WARM_UP_CONFIG_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=True)


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("Config file not found")


def load_warmup_config():
    try:
        with open(WARM_UP_CONFIG_FILE, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("Warmup Config file not found")


def load_add_liquidity_config():
    try:
        with open(LIQUIDITY_CONFIG_FILE, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("Config file not found")


def load_stake_stg_config():
    try:
        with open(STAKE_STG_CONFIG_FILE, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("Config file not found")


def get_all_wallets_logs_data():
    files_dir = WALLET_LOGS_DIR
    all_data = []

    for filename in os.listdir(files_dir):
        if filename.endswith(".json"):
            # Open the file and load the data
            with open(os.path.join(files_dir, filename)) as file:
                file_data = json.load(file)
            # Add the data to the list
            all_data.append(file_data)

    combined_data = []
    for data in all_data:
        combined_data.append(data)

    return combined_data


def save_summary_log_file():
    data = get_all_wallets_logs_data()
    path = os.path.join(MAIN_DIR, 'summary_logs.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
        logger.info(f'Summary log file created in local directory\n')
