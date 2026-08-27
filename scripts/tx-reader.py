import sys
from web3 import Web3

# STEP 1 — Multi-network configuration lookup table
NETWORKS = {
    "ethereum_mainnet": "https://mainnet.infura.io/v3/YOUR_KEY",
    "polygon_mainnet": "https://polygon-mainnet.infura.io/v3/YOUR_KEY",
}

def get_web3_connection(network_name):
    """Look up the network in NETWORKS and return a connected Web3 instance."""
    if network_name not in NETWORKS:
        raise ValueError(f"Unknown network: {network_name}")
    endpoint = NETWORKS[network_name]
    return Web3(Web3.HTTPProvider(endpoint))

# STEP 2 — Simulated cross-network transaction fetch
def fetch_tx_from_network(tx_hash, network_name):
    print(f"Simulating fetch from {network_name} for tx {tx_hash}")
    w3 = get_web3_connection(network_name)
    return get_transaction_details(w3, tx_hash)  # existing function from tx-reader.py

if __name__ == "__main__":
    # Reads network name from command line, e.g.: python tx-reader.py polygon_mainnet
    network_to_use = sys.argv[1] if len(sys.argv) > 1 else "ethereum_mainnet"
    print(f"Using network: {network_to_use}")