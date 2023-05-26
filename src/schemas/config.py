from typing import Union

from pydantic import BaseSettings


class ConfigSchema(BaseSettings):
    bridge_option: str = ""
    source_chain: str = ""
    target_chain: str = ""
    coin_to_transfer: str = ""
    min_bridge_amount: Union[float, str] = 0
    max_bridge_amount: Union[float, str] = 0
    min_delay_seconds: int = 0
    max_delay_seconds: int = 0
    gas_price: Union[float, str] = 0
    gas_limit: int = 0
    slippage: float = 0
    address_to_send: str = ""
    custom_gas_price: bool = False
    send_to_one_address: bool = False
    send_all_balance: bool = False
    test_mode: bool = True


class WarmUpConfigSchema(BaseSettings):
    chain_options: list = []
    coin_to_transfer: str = ""
    min_amount_to_transfer: float = 0
    max_amount_to_transfer: float = 0
    min_delay_seconds: int = 0
    max_delay_seconds: int = 0
    max_gas_limit: int = 0
    slippage: float = 0
    shuffle_wallets_order: bool = False
    test_mode: bool = True


