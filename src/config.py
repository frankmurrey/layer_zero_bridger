import time

from src.files_manager import load_config
from src.schemas.config import ConfigSchema

from loguru import logger

CONFIG_FILE_DATA: dict = load_config()


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


def print_config(config: ConfigSchema, log_text: str):
    logger.info(f'Config:')
    for key, value in config.__dict__.items():
        logger.warning(f'{key}: {value}')
    logger.info(log_text)
    logger.info("Press 'Ctrl+C' to stop the process\n")
    time.sleep(5)

