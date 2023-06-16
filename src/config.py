import time

from src.files_manager import load_config, load_warmup_config, load_add_liquidity_config, load_stake_stg_config
from src.schemas.config import ConfigSchema, WarmUpConfigSchema
from src.schemas.stake import AddLiquidityConfig, StakeStgConfig

from sys import stderr

from loguru import logger

CONFIG_STAKE_STG_DATA: dict = load_stake_stg_config()
CONFIG_ADD_LIQUIDITY_DATA: dict = load_add_liquidity_config()
CONFIG_FILE_DATA: dict = load_config()
WARMUP_CONFIG_FILE_DATA: dict = load_warmup_config()


def get_stake_stg_config() -> StakeStgConfig:
    try:
        return StakeStgConfig(**CONFIG_STAKE_STG_DATA)
    except Exception as e:
        logger.error(f'Error while loading config: {e}')
        return StakeStgConfig()


def get_add_liquidity_config() -> AddLiquidityConfig:
    try:
        return AddLiquidityConfig(**CONFIG_ADD_LIQUIDITY_DATA)
    except Exception as e:
        logger.error(f'Error while loading config: {e}')
        return AddLiquidityConfig()


def get_warmup_config() -> WarmUpConfigSchema:
    try:
        return WarmUpConfigSchema(**WARMUP_CONFIG_FILE_DATA)
    except Exception as e:
        logger.error(f'Error while loading warmup_config: {e}')
        return WarmUpConfigSchema()


def get_config() -> ConfigSchema:
    try:
        return ConfigSchema(**CONFIG_FILE_DATA)
    except Exception as e:
        logger.error(f'Error while loading config: {e}')
        return ConfigSchema()


def get_config_from_dict(config_dict: dict) -> ConfigSchema:
    try:
        return ConfigSchema(**config_dict)
    except Exception as e:
        logger.error(f'Error while loading config: {e}')
        return ConfigSchema()


def get_warmup_config_from_dict(config_dict: dict) -> WarmUpConfigSchema:
    try:
        return WarmUpConfigSchema(**config_dict)
    except Exception as e:
        logger.error(f'Error while loading config: {e}')
        return WarmUpConfigSchema()


def get_add_liquidity_config_from_dict(config_dict: dict) -> AddLiquidityConfig:
    try:
        return AddLiquidityConfig(**config_dict)
    except Exception as e:
        logger.error(f'Error while loading config: {e}')
        return AddLiquidityConfig()


def get_stake_stg_config_from_dict(config_dict: dict) -> StakeStgConfig:
    try:
        return StakeStgConfig(**config_dict)
    except Exception as e:
        logger.error(f'Error while loading config: {e}')
        return StakeStgConfig()


def print_config(config):
    delay_seconds = 2

    logger.remove()
    logger.add(stderr,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{line: <3}</cyan>"
                      " - <level>{message}</level>")
    logger.info(f'Config:')
    for key, value in config.__dict__.items():
        logger.warning(f'{key}: {value}')

    logger.info(f"Starting bridge in ({delay_seconds}) seconds")
    logger.info("Press 'Ctrl+C' to stop the process\n")
    logger.debug('Created by: https://github.com/frankmurrey (tg @shnubjack)\n')
    time.sleep(delay_seconds)

