import time

from src.files_manager import load_config, load_warmup_config
from src.schemas.config import ConfigSchema, WarmUpConfigSchema

from loguru import logger

CONFIG_FILE_DATA: dict = load_config()
WARMUP_CONFIG_FILE_DATA: dict = load_warmup_config()


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


def print_config(config, delay_seconds: int = 10):
    logger.info(f'Config:')
    for key, value in config.__dict__.items():
        logger.warning(f'{key}: {value}')
    logger.info(f"Starting bridge in ({delay_seconds}) seconds")
    logger.info("Press 'Ctrl+C' to stop the process\n")
    logger.debug('Created by: https://github.com/frankmurrey (tg @shnubjack)\n')
    time.sleep(delay_seconds)

