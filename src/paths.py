import pathlib
import os

MAIN_DIR = os.path.join(pathlib.Path(__file__).parent.parent.resolve())
CONFIG_FILE = os.path.join(MAIN_DIR, "config_manual.yaml")
WARM_UP_CONFIG_FILE = os.path.join(MAIN_DIR, "config_warmup.yaml")
CONTRACTS_DIR = os.path.join(MAIN_DIR, "contracts")
WALLET_LOGS_DIR = os.path.join(MAIN_DIR, "wallet_logs")

WALLETS_FILE = os.path.join(MAIN_DIR, "evm_wallets.txt")
APTOS_WALLETS_FILE = os.path.join(MAIN_DIR, "aptos_addresses.txt")
RPCS_FILE = os.path.join(CONTRACTS_DIR, "rpcs.json")


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
    CORE_DAO_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "core_dao_router.abi")


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


class CoreDaoDir:
    CHAIN_DIR = os.path.join(CONTRACTS_DIR, "core_dao")
    ABIS_DIR = os.path.join(CHAIN_DIR, "abis")
    CORE_DAO_ROUTER_ABI_FILE = os.path.join(ABIS_DIR, "core_dao_router.abi")
    USDT_ABI_FILE = os.path.join(ABIS_DIR, "usdt.abi")



OPTIMISM_ROUTER_ABI_FILE = os.path.join(CONTRACTS_DIR, "optimism", "router.abi")
OPTIMISM_ETH_ROUTER_ABI_FILE = os.path.join(CONTRACTS_DIR, "optimism", "eth_router.abi")