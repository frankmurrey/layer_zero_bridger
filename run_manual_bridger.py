import time

from bridge_swap.eth_bridge import eth_mass_transfer
from bridge_swap.token_bridge import token_mass_transfer, token_mass_approve
from bridge_swap.bridge_to_aptos import eth_mass_transfer_to_aptos, token_mass_transfer_to_aptos
from bridge_swap.bridge_to_aptos import token_mass_approve_to_aptos

from src.config import get_config
from src.bridge_manager import BridgeManager


from loguru import logger


def run_config():
    config = get_config()
    bridge_manager = BridgeManager(input_data=config)
    error_msg = bridge_manager.check_if_route_eligible()
    if error_msg is not True:
        logger.error(error_msg)
        return

    if config.target_chain == "Aptos":
        if config.coin_to_transfer == "Ethereum":
            eth_mass_transfer_to_aptos(config_data=config)
        else:
            token_mass_approve_to_aptos(config_data=config)
            time.sleep(2)
            token_mass_transfer_to_aptos(config_data=config)

    if config.target_chain != "Aptos":
        if config.coin_to_transfer == "Ethereum":
            eth_mass_transfer(config_data=config)
        else:
            token_mass_approve(config_data=config)
            time.sleep(2)
            token_mass_transfer(config_data=config)


if __name__ == '__main__':
    run_config()
