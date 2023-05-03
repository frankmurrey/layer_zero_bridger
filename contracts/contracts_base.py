from web3 import Web3


class ContractsBase:
    pass


class Token:
    def __init__(self, name: str, abi: str, address, pool_id: int):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.abi = abi
        self.pool_id = pool_id
