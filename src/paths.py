import pathlib
import os

MAIN_DIR = os.path.join(pathlib.Path(__file__).parent.parent.resolve())
CONFIG_FILE = os.path.join(MAIN_DIR, "config.yaml")
CONTRACTS_DIR = os.path.join(MAIN_DIR, "contracts")

WALLETS_FILE = os.path.join(MAIN_DIR, "evm_wallets.txt")
APTOS_WALLETS_FILE = os.path.join(MAIN_DIR, "aptos_addresses.txt")


class ArbDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "arbitrum")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "router.abi")
    ETH_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "eth_router.abi")
    USDC_ABI_FILE = os.path.join(ABIS_DIR, "usdc.abi")
    USDT_ABI_FILE = os.path.join(ABIS_DIR, "usdt.abi")
    APT_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "aptos_router.abi")
    ENDPOINT_ABI_FILE = os.path.join(ABIS_DIR, "endpoint.abi")


class OptDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "optimism")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "router.abi")
    ETH_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "eth_router.abi")
    USDC_ABI_FILE = os.path.join(ABIS_DIR, "usdc.abi")
    USDT_ABI_FILE = os.path.join(ABIS_DIR, "usdt.abi")
    APT_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "aptos_router.abi")
    ENDPOINT_ABI_FILE = os.path.join(ABIS_DIR, "endpoint.abi")


class BscDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "bsc")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "router.abi")
    USDT_ABI_FILE = os.path.join(ABIS_DIR, "usdt.abi")
    APT_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "aptos_router.abi")
    ENDPOINT_ABI_FILE = os.path.join(ABIS_DIR, "endpoint.abi")


class PolygonDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "polygon")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "router.abi")
    USDT_ABI_FILE = os.path.join(ABIS_DIR, "usdt.abi")
    USDC_ABI_FILE = os.path.join(ABIS_DIR, "usdc.abi")
    APT_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "aptos_router.abi")
    ENDPOINT_ABI_FILE = os.path.join(ABIS_DIR, "endpoint.abi")


class AvalancheDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "avalanche")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "router.abi")
    USDT_ABI_FILE = os.path.join(ABIS_DIR, "usdt.abi")
    USDC_ABI_FILE = os.path.join(ABIS_DIR, "usdc.abi")
    APT_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "aptos_router.abi")
    ENDPOINT_ABI_FILE = os.path.join(ABIS_DIR, "endpoint.abi")


class EthereumDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "ethereum")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "router.abi")
    ETH_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "eth_router.abi")
    USDT_ABI_FILE = os.path.join(ABIS_DIR, "usdt.abi")
    USDC_ABI_FILE = os.path.join(ABIS_DIR, "usdc.abi")
    APT_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "aptos_router.abi")
    ENDPOINT_ABI_FILE = os.path.join(ABIS_DIR, "endpoint.abi")


class FantomDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "fantom")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "router.abi")
    USDC_ABI_FILE = os.path.join(ABIS_DIR, "usdc.abi")


OPTIMISM_ROUTER_ABI_FILE = os.path.join(CONTRACTS_DIR, "optimism", "router.abi")
OPTIMISM_ETH_ROUTER_ABI_FILE = os.path.join(CONTRACTS_DIR, "optimism", "eth_router.abi")