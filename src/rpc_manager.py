import time

from contracts.rpcs import RPC

from web3 import Web3
from loguru import logger


class RpcValidator:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            logger.debug(f"Created by https://github.com/frankmurrey (tg @shnubjack)\n")
            cls.instance = super(RpcValidator, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.rpc_list = RPC
        self._validated_rpcs = None

    @property
    def validated_rpcs(self):
        if not hasattr(self.__class__, '_validated_rpcs'):
            self.__class__._validated_rpcs = self.get_all_valid_rpcs()
        return self.__class__._validated_rpcs

    def check_rpc(self, rpc_url, rpc_name):
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        time_start = time.time()
        rpc_response = web3.is_connected()
        time_end = time.time()
        if rpc_response is True:
            logger.info(f"Valid ({round(time_end - time_start, 3)} sec) - {rpc_name.title()} [{rpc_url}]")
            return True
        else:
            logger.error(f"Invalid - {rpc_name.title()} [{rpc_url}]")
            return False

    def get_all_valid_rpcs(self):
        logger.info("Checking all required rpcs")
        valid_rpcs = {}

        for rpc_name in self.rpc_list:
            rpc_urls = self.rpc_list[rpc_name]
            rpc_list = []

            for rpc_url in rpc_urls:
                try:
                    status = self.check_rpc(rpc_url=rpc_url, rpc_name=rpc_name)
                except AssertionError:
                    logger.error(f"Invalid - {rpc_name.title()} [{rpc_url}]")
                    status = False
                if status is True:
                    rpc_list.append(rpc_url)
            valid_rpcs[rpc_name] = rpc_list

        logger.info(f"RPC check finished, validated: {len(valid_rpcs)}\n")

        return valid_rpcs

    def check_if_required_rpcs_available(self, chain_options: list):
        for chain_name in chain_options:
            for chain in self.validated_rpcs:
                if chain_name == chain:
                    if len(self.validated_rpcs[chain]) == 0:
                        logger.error(f"Provide at least one valid rpc for {chain_name}")
                        return False
                    else:
                        return True