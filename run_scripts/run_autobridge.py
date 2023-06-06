from src.config import get_warmup_config
from src.bridge_manager import WarmUpRouteValidator
from src.templates import check_all_temp_files
from src.paths import WARM_UP_CONFIG_FILE

from bridge_swap.warm_up.main import initialize_all_wallets, warm_up, save_summary_log_file

from loguru import logger

if __name__ == '__main__':
    temp_files_status = check_all_temp_files(file_path=WARM_UP_CONFIG_FILE)
    if temp_files_status is False:
        logger.warning(f"Please fill the config file and restart program after")
        exit(1)

    warmup_config = get_warmup_config()
    warmup_route_validator = WarmUpRouteValidator(input_data=warmup_config)
    route_status = warmup_route_validator.check_route()

    if route_status is not True:
        logger.error(route_status)
        exit(1)

    initialize_all_wallets()
    warm_up()
    save_summary_log_file()
