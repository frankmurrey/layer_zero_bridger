from datetime import datetime

from pydantic import BaseSettings


class WarmUpWalletSchema(BaseSettings):
    address: str = None
    private_key: str = None
    last_bridge_time: int = None
    last_bridge_date: str = None
    last_bridge_status: bool = None
    last_bridge_tx_hash: str = None
