from src.paths import CONFIG_FILE, LIQUIDITY_CONFIG_FILE, STAKE_STG_CONFIG_FILE, WARM_UP_CONFIG_FILE
from src.paths import RPCS_FILE

from src.schemas.stake import StakeStgConfig, AddLiquidityConfig
from src.schemas.config import ConfigSchema, WarmUpConfigSchema

from src.files_manager import check_if_file_exists
from src.files_manager import create_yaml_file, create_json_file

from loguru import logger


def get_temp_files_status() -> bool:
    all_paths = [CONFIG_FILE, LIQUIDITY_CONFIG_FILE, STAKE_STG_CONFIG_FILE, WARM_UP_CONFIG_FILE, RPCS_FILE]

    for path in all_paths:
        if not check_if_file_exists(path):
            return False


def create_all_temp_files():
    if not check_if_file_exists(CONFIG_FILE):
        logger.info("[config_manual.yaml] - file not found, creating...")
        create_yaml_file(CONFIG_FILE, ConfigSchema().dict())

    if not check_if_file_exists(LIQUIDITY_CONFIG_FILE):
        logger.info("[config_liquidity.yaml] - file not found, creating...")
        create_yaml_file(LIQUIDITY_CONFIG_FILE, AddLiquidityConfig().dict())

    if not check_if_file_exists(STAKE_STG_CONFIG_FILE):
        logger.info("[config_stake_stg.yaml] - file not found, creating...")
        create_yaml_file(STAKE_STG_CONFIG_FILE, StakeStgConfig().dict())

    if not check_if_file_exists(WARM_UP_CONFIG_FILE):
        logger.info("[config_warmup.yaml] - file not found, creating...")
        create_yaml_file(WARM_UP_CONFIG_FILE, WarmUpConfigSchema().dict())


def create_rpcs_file():
    if not check_if_file_exists(RPCS_FILE):
        logger.info("[rpcs.json] - file not found, creating...")
        create_json_file(RPCS_FILE, Templates().rpcs)


def check_all_temp_files(file_path: str = None):
    if file_path is not None:
        files_status = check_if_file_exists(file_path)
    else:
        files_status = True

    all_files_status = get_temp_files_status()
    if all_files_status is False:
        create_all_temp_files()

    return files_status


class Templates:
    @property
    def rpcs(self):
        json_data = {
            "Arbitrum": [
                "https://1rpc.io/arb",
                "https://arbitrum-one.public.blastapi.io"
            ],
            "Avalanche": [
                "https://rpc.ankr.com/avalanche"
            ],
            "BSC": [
                "https://rpc.ankr.com/bsc"
            ],
            "Ethereum": [
                "https://rpc.ankr.com/eth"
            ],
            "Fantom": [
                "https://rpc.ankr.com/fantom"
            ],
            "Polygon": [
                "https://rpc.ankr.com/polygon"
            ],
            "Optimism": [
                "https://rpc.ankr.com/optimism"
            ],
            "CoreDao": [
                "https://rpc.coredao.org"
            ]
        }

        return json_data
