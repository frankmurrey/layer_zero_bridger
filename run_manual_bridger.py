from src.config import get_config
from src.bridge_manager import BridgeManager

from bridge_swap.bridge_runner import run_bridge


from loguru import logger


def run_config():
    config = get_config()
    bridge_manager = BridgeManager(input_data=config)
    error_msg = bridge_manager.check_if_route_eligible()
    if error_msg is not True:
        logger.error(error_msg)
        return

    run_bridge(config_data=config)


if __name__ == '__main__':
    run_config()
