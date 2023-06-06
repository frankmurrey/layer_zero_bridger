from src.config import get_stake_stg_config
from src.stake_manager import StakeManager
from src.templates import check_all_temp_files
from src.paths import STAKE_STG_CONFIG_FILE

from stake.stake_stg.main import mass_stake_stg

from loguru import logger


def run_config():
    temp_files_status = check_all_temp_files(file_path=STAKE_STG_CONFIG_FILE)
    if temp_files_status is False:
        logger.warning(f"Please fill the config file and restart program after")
        exit(1)

    config = get_stake_stg_config()
    stake_manager = StakeManager(input_data=config)
    error_msg = stake_manager.check_if_route_eligible()

    if error_msg is not True:
        logger.error(error_msg)
        exit(1)

    mass_stake_stg(config=config)


if __name__ == '__main__':
    run_config()