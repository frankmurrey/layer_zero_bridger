from src.config import get_config
from src.bridge_manager import BridgeManager
from src.templates import check_all_temp_files
from src.paths import CONFIG_FILE

from bridge_swap.bridge_runner import run_bridge

from loguru import logger


def run_config():
    temp_files_status = check_all_temp_files(file_path=CONFIG_FILE)
    if temp_files_status is False:
        logger.warning(f"Please fill the config file and restart program after")
        exit(1)

    config = get_config()
    bridge_manager = BridgeManager(input_data=config)
    error_msg = bridge_manager.check_if_route_eligible()
    if error_msg is not True:
        logger.error(error_msg)
        exit(1)

    run_bridge(config_data=config)


if __name__ == '__main__':
    run_config()
