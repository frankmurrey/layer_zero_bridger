import random
import time

from datetime import datetime, timedelta

from bridge_swap.base_bridge import BridgeBase
from src.files_manager import read_evm_wallets_from_file
from src.schemas.config import ConfigSchema
from src.config import print_config
from src.rpc_manager import RpcValidator

from web3 import Web3
from loguru import logger


def eth_mass_transfer(config_data: ConfigSchema):
    print_config(config=config_data)

    rpc_validator = RpcValidator()
    rpcs = rpc_validator.validated_rpcs

    eth_bridge = EthBridgeManual(config=config_data)
    wallets = read_evm_wallets_from_file()
    wallet_number = 1
    wallets_amount = len(wallets)
    for wallet in wallets:
        blured_wallet = eth_bridge.blur_private_key(private_key=wallet)
        wallet_address = eth_bridge.get_wallet_address(private_key=wallet)
        logger.info(f"[{wallet_number}] - {wallet_address}")
        logger.info(f"Got wallet pk /{blured_wallet}/")

        bridge_status = eth_bridge.transfer(private_key=wallet)

        if wallet_number == wallets_amount:
            logger.info(f"Bridge process is finished\n")
            break

        wallet_number += 1

        if bridge_status is not None:
            time_delay = random.randint(config_data.min_delay_seconds, config_data.max_delay_seconds)
        else:
            time_delay = 3

        if time_delay == 0:
            time.sleep(0.3)
            continue

        delta = timedelta(seconds=time_delay)
        result_datetime = datetime.now() + delta

        logger.info(f"Waiting {time_delay} seconds, next wallet bridge {result_datetime}\n")
        time.sleep(time_delay)


class EthBridgeManual(BridgeBase):
    def __init__(self, config: ConfigSchema):
        super().__init__(config=config)

    def transfer(self, private_key, wallet_number=None):
        source_wallet_address = self.get_wallet_address(private_key=private_key)
        wallet_eth_balance = self.get_eth_balance(source_wallet_address)
        wallet_address = self.get_wallet_address(private_key=private_key)
        eth_amount_out_wei = self.get_random_amount_out(min_amount=self.min_bridge_amount,
                                                        max_amount=self.max_bridge_amount)
        eth_amount_out_decimals = Web3.from_wei(eth_amount_out_wei, 'ether')

        if wallet_eth_balance < eth_amount_out_wei:
            logger.error(f"Not enough native (Need: {eth_amount_out_decimals} ETH) "
                         f"to bridge. Balance: {Web3.from_wei(wallet_eth_balance, 'ether')} ETH")
            return

        if self.config_data.send_to_one_address is True:
            dst_wallet_address = Web3.to_checksum_address(self.config_data.address_to_send)
        else:
            dst_wallet_address = wallet_address

        txn = self.build_eth_bridge_tx(wallet_address=wallet_address,
                                       dst_wallet_address=dst_wallet_address,
                                       amount_out=eth_amount_out_wei,
                                       chain_id=self.target_chain.chain_id)
        try:
            estimated_gas_limit = self.get_estimate_gas(transaction=txn)

            if self.config_data.gas_limit > estimated_gas_limit:
                txn['gas'] = estimated_gas_limit

            if self.config_data.test_mode is True:
                logger.info(f"Estimated gas limit for {self.source_chain.name} → "
                            f"{self.target_chain.name} "
                            f"ETH bridge: {estimated_gas_limit}")
                return

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            if self.config_data.wait_for_confirmation is True:
                time_out = self.config_data.confirmation_timeout_seconds
                tx_receipt = self.wait_for_tx_receipt(tx_hash=tx_hash, time_out=time_out)
                if tx_receipt['status'] == 1:
                    logger.success(
                        f"{self.config_data.source_chain} → {self.config_data.target_chain}"
                        f" ({eth_amount_out_decimals} ETH) bridge transaction success: {tx_hash.hex()}")
                    return tx_hash.hex()
                else:
                    logger.error(f"Transaction is not success: {tx_hash.hex()}")

            else:
                logger.success(
                    f"{self.config_data.source_chain} → {self.config_data.target_chain} "
                    f"({eth_amount_out_decimals} ETH) bridge transaction sent: {tx_hash.hex()}")
                return tx_hash.hex()

        except Exception as e:
            logger.error(f"Error while sending ETH bridge txn: {e}")
            return
