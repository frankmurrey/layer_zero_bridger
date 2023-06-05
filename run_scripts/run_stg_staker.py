from src.config import get_stake_stg_config
from src.stake_manager import StakeManager

from stake.stake_stg.main import mass_stake_stg

from loguru import logger


def run_config():
    config = get_stake_stg_config()
    stake_manager = StakeManager(input_data=config)
    error_msg = stake_manager.check_if_route_eligible()

    if error_msg is not True:
        logger.error(error_msg)
        exit(1)

    mass_stake_stg(config=config)


if __name__ == '__main__':
    run_config()