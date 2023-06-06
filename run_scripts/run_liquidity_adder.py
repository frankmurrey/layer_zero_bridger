from src.config import get_add_liquidity_config
from src.stake_manager import LiquidityManager
from src.templates import check_all_temp_files
from src.paths import LIQUIDITY_CONFIG_FILE

from stake.add_liquidity.main import mass_add_liquidity

from loguru import logger


def run_config():
    temp_files_status = check_all_temp_files(file_path=LIQUIDITY_CONFIG_FILE)
    if temp_files_status is False:
        logger.warning(f"Please fill the config file and restart program after")
        exit(1)

    config = get_add_liquidity_config()
    stake_manager = LiquidityManager(input_data=config)
    error_msg = stake_manager.check_if_route_eligible()

    if error_msg is not True:
        logger.error(error_msg)
        exit(1)

    mass_add_liquidity(config=config)


if __name__ == '__main__':
    run_config()