from typing import Union

from pydantic import BaseSettings


class ConfigSchema(BaseSettings):
    bridge_option: str = ""
    source_chain: str = ""
    target_chain: str = ""
    source_coin_to_transfer: str = ""
    target_coin_to_transfer: Union[str, None] = ""
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
    wait_for_confirmation: bool = False
    confirmation_timeout_seconds: Union[float, str] = 0


class WarmUpConfigSchema(BaseSettings):
    chain_options: list = []
    coin_to_transfer: str = ""
    min_amount_to_transfer: Union[float, str, None] = 0
    max_amount_to_transfer: Union[float, str, None] = 0
    min_delay_seconds: int = 0
    max_delay_seconds: int = 0
    max_gas_limit: int = 0
    slippage: float = 0
    send_all_balance: bool = False
    shuffle_wallets_order: bool = False
    test_mode: bool = True
    wait_for_confirmation: bool = False
    confirmation_timeout_seconds: Union[float, str] = 0


