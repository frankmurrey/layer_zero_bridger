from typing import Union

from pydantic import BaseSettings


class ConfigSchema(BaseSettings):
    source_chain: str = ""
    target_chain: str = ""
    min_bridge_amount: float = 0
    max_bridge_amount: float = 0
    coin_to_transfer: str = ""
    gas_price: Union[float, str] = 0
    gas_limit: int = 0
    slippage: float = 0
    custom_gas_price: bool = False
    test_mode: bool = False
    send_to_one_address: bool = False
    address_to_send: str = ""
