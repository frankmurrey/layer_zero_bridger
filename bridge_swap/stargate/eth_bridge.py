import random
import time

from bridge_swap.base_bridge import BridgeBase
from src.files_manager import read_evm_wallets_from_file
from src.schemas.config import ConfigSchema
from src.config import print_config

from web3 import Web3
from loguru import logger


def eth_mass_transfer(config_data: ConfigSchema):
    print_config(config=config_data,
                 delay_seconds=10)

    eth_bridge = EthBridgeManual(config=config_data)
    wallets = read_evm_wallets_from_file()
    wallet_number = 1
    for wallet in wallets:
        bridge_status = eth_bridge.transfer(private_key=wallet, wallet_number=wallet_number)
        wallet_number += 1

        if bridge_status is not None:
            time_delay = random.randint(config_data.min_delay_seconds, config_data.max_delay_seconds)
        else:
            time_delay = 3

        if time_delay == 0:
            time.sleep(0.3)
            continue
        logger.info(f"Waiting {time_delay} seconds ({round((time_delay / 60), 2)} min) before next wallet bridge\n")
        time.sleep(time_delay)


class EthBridgeManual(BridgeBase):
    def __init__(self, config: ConfigSchema):
        super().__init__(config=config)

    def transfer(self, private_key, wallet_number=None):
        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_eth_balance = self.get_eth_balance(source_wallet_address)
        wallet_address = self.get_wallet_address(private_key=private_key)
        eth_amount_out = self.get_random_amount_out(min_amount=self.min_bridge_amount,
                                                    max_amount=self.max_bridge_amount)

        if wallet_number is None:
            wallet_number = ""

        if wallet_eth_balance < eth_amount_out:
            logger.error(f"[{wallet_number}] [{source_wallet_address}] - not enough native"
                         f" ({Web3.from_wei(eth_amount_out, 'ether')} ETH) "
                         f"to bridge. Balance: {Web3.from_wei(wallet_eth_balance, 'ether')} ETH")
            return

        if self.config_data.send_to_one_address is True:
            dst_wallet_address = Web3.to_checksum_address(self.config_data.address_to_send)
        else:
            dst_wallet_address = wallet_address

        txn = self.build_eth_bridge_tx(wallet_address=wallet_address,
                                       dst_wallet_address=dst_wallet_address,
                                       amount_out=eth_amount_out,
                                       chain_id=self.target_chain.chain_id)
        try:
            estimated_gas_limit = self.get_estimate_gas(transaction=txn)

            if self.config_data.gas_limit > estimated_gas_limit:
                txn['gas'] = estimated_gas_limit

            if self.config_data.test_mode is True:
                logger.info(f"[{wallet_number}] [{source_wallet_address}] - Estimated gas limit for {self.source_chain.name} → "
                            f"{self.target_chain.name} "
                            f"ETH bridge: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"[{wallet_number}] [{source_wallet_address}] - Transaction sent: {tx_hash.hex()}")

            return tx_hash.hex()
        except Exception as e:
            logger.error(f"[{wallet_number}] [{source_wallet_address}] - Error while sending ETH bridge txn: {e}")
            return
