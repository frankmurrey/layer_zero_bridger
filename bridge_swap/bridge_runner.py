from src.schemas.config import ConfigSchema

from bridge_swap.stargate.token_bridge import token_mass_transfer as stargate_token_mass_transfer
from bridge_swap.stargate.eth_bridge import eth_mass_transfer as stargate_eth_mass_transfer
from bridge_swap.core.token_bridge import core_mass_transfer as core_token_mass_transfer
from bridge_swap.aptos.bridge_to_aptos import eth_mass_transfer_to_aptos as aptos_eth_mass_transfer
from bridge_swap.aptos.bridge_to_aptos import token_mass_transfer_to_aptos as aptos_token_mass_transfer


def run_bridge(config_data: ConfigSchema):
    bridge_name = config_data.bridge_option
    coin_to_transfer = config_data.source_coin_to_transfer

    if bridge_name.lower() == 'stargate':
        if coin_to_transfer.lower() == 'ethereum':
            stargate_eth_mass_transfer(config_data)
        else:
            stargate_token_mass_transfer(config_data)

    elif bridge_name.lower() == 'coredao':
        core_token_mass_transfer(config_data)

    elif bridge_name.lower() == 'aptos':
        if coin_to_transfer.lower() == 'ethereum':
            aptos_eth_mass_transfer(config_data)
        else:
            aptos_token_mass_transfer(config_data)