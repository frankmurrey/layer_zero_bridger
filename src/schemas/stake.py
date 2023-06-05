from typing import Union

from pydantic import BaseSettings


class AddLiquidityConfig(BaseSettings):
    source_chain: str = ""
    coin_to_stake: str = ""
    min_amount_to_stake: Union[float, str, None] = 0
    max_amount_to_stake: Union[float, str, None] = 0
    stake_all_balance: bool = False
    min_delay_seconds: int = 0
    max_delay_seconds: int = 0
    gas_limit: int = 0
    test_mode: bool = True


class StakeStgConfig(BaseSettings):
    source_chain: str = ""
    min_amount_to_stake: Union[float, str, None] = 0
    max_amount_to_stake: Union[float, str, None] = 0
    stake_all_balance: bool = False
    lock_period_months: Union[int, str, None] = 0
    min_delay_seconds: Union[int, str, None] = 0
    max_delay_seconds: Union[int, str, None] = 0
    gas_limit: int = 0
    test_mode: bool = True
