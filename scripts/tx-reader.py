import os
import sys
from datetime import datetime, timezone

from eth_utils import event_abi_to_log_topic
from web3 import Web3
from web3._utils.events import get_event_data


# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

CONFIRMATION_DEPTH = 12

# Read the key from the environment instead of committing it to GitHub.
INFURA_API_KEY = os.getenv("INFURA_API_KEY")

NETWORKS = {
    "ethereum_mainnet": (
        f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"
        if INFURA_API_KEY
        else None
    ),
    "polygon_mainnet": (
        f"https://polygon-mainnet.infura.io/v3/{INFURA_API_KEY}"
        if INFURA_API_KEY
        else None
    ),
}

# Addresses that the reconciliation monitor should track.
TARGET_ADDRESSES = {
    Web3.to_checksum_address(
        "0x28c6c06298d514db089934071355e5743bf21d60"
    ),
}

# Avoid fetching the same block timestamp repeatedly.
_block_time_cache = {}


# A simplified ABI containing the ERC-20 Transfer event.
# More event definitions can be added to this list later.
GENERIC_EVENT_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "to",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256",
            },
        ],
        "name": "Transfer",
        "type": "event",
    }
]


# -------------------------------------------------------------------
# NETWORK CONNECTION
# -------------------------------------------------------------------

def get_web3_connection(network_name):
    """
    Return a connected Web3 instance for the selected network.
    """

    if network_name not in NETWORKS:
        available_networks = ", ".join(NETWORKS.keys())

        raise ValueError(
            f"Unknown network: {network_name}. "
            f"Available networks: {available_networks}"
        )

    endpoint = NETWORKS[network_name]

    if not endpoint:
        raise ValueError(
            "INFURA_API_KEY is not configured in the environment."
        )

    w3 = Web3(Web3.HTTPProvider(endpoint))

    if not w3.is_connected():
        raise ConnectionError(
            f"Could not connect to network: {network_name}"
        )

    return w3


# -------------------------------------------------------------------
# BLOCK ENRICHMENT AND RECONCILIATION GUARDS
# -------------------------------------------------------------------

def get_block_time(w3, block_number):
    """
    Return a timezone-aware UTC datetime for a block.

    Results are cached so that multiple logs from the same block do not
    cause repeated node requests.
    """

    if block_number not in _block_time_cache:
        block = w3.eth.get_block(block_number)

        _block_time_cache[block_number] = datetime.fromtimestamp(
            block["timestamp"],
            tz=timezone.utc,
        )

    return _block_time_cache[block_number]


def is_confirmed(w3, block_number, depth=CONFIRMATION_DEPTH):
    """
    Return True when a block is buried by at least the requested depth.
    """

    current_block = w3.eth.block_number
    return (current_block - block_number) >= depth


def touches_target(from_addr, to_addr, targets=TARGET_ADDRESSES):
    """
    Return True when either side of a transfer is an address we track.

    If the target collection is empty, all transfers are accepted.
    """

    if not targets:
        return True

    if not from_addr or not to_addr:
        return False

    return (
        Web3.to_checksum_address(from_addr) in targets
        or Web3.to_checksum_address(to_addr) in targets
    )


# -------------------------------------------------------------------
# GENERIC EVENT DECODING
# -------------------------------------------------------------------

def build_event_topic_map(contract_abi):
    """
    Build a lookup table connecting topic hashes to event ABI entries.

    The first topic in a non-anonymous event log identifies the event.
    """

    topic_map = {}

    for abi_item in contract_abi:
        if abi_item.get("type") != "event":
            continue

        topic = event_abi_to_log_topic(abi_item)
        topic_map[topic] = abi_item

    return topic_map


def decode_event_logs(w3, receipt, contract_abi):
    """
    Decode any receipt logs whose event definitions exist in contract_abi.

    Unrecognized logs are reported as undecodable rather than causing
    the entire transaction reader to fail.
    """

    topic_map = build_event_topic_map(contract_abi)
    decoded_records = []

    for log in receipt["logs"]:
        topics = log.get("topics", [])

        if not topics:
            print(
                f"Undecodable log detected at index "
                f"{log.get('logIndex')}."
            )
            continue

        event_abi = topic_map.get(topics[0])

        if event_abi is None:
            print(
                f"Undecodable log detected at index "
                f"{log.get('logIndex')}."
            )
            continue

        try:
            decoded_log = get_event_data(
                w3.codec,
                event_abi,
                log,
            )
        except (ValueError, TypeError, KeyError) as error:
            print(
                f"Undecodable log detected at index "
                f"{log.get('logIndex')}: {error}"
            )
            continue

        event_name = decoded_log["event"]
        event_args = dict(decoded_log["args"])

        print(f"\nDecoded event: {event_name}")
        print(f"Arguments: {event_args}")

        block_number = log["blockNumber"]

        # Confirmation guard
        if not is_confirmed(w3, block_number):
            print(f"SKIPPED (unconfirmed) block {block_number}")
            continue

        # Target filtering currently applies to Transfer-style events
        # containing "from" and "to" arguments.
        if event_name == "Transfer":
            from_addr = event_args.get("from")
            to_addr = event_args.get("to")

            if not touches_target(from_addr, to_addr):
                print("SKIPPED (does not touch a target address)")
                continue

        block_time = get_block_time(w3, block_number)

        record = {
    "event_name": event_name,
    "tx_hash": log["transactionHash"].hex(),
    "log_index": log["logIndex"],
    "block_number": block_number,
    "block_time_utc": block_time.isoformat(),
    "contract_address": Web3.to_checksum_address(
        log["address"]
    ),
    "from": Web3.to_checksum_address(from_addr),
    "to": Web3.to_checksum_address(to_addr),
    "raw_value": raw_value,
}
``

        decoded_records.append(record)
        print(f"Reconciliation record: {record}")

    return decoded_records


# -------------------------------------------------------------------
# TRANSACTION READER
# -------------------------------------------------------------------

def read_transaction(w3, tx_hash, contract_abi):
    """
    Fetch a transaction and receipt, then decode its known event logs.
    """

    if not Web3.is_hex(tx_hash) or len(tx_hash) != 66:
        raise ValueError(
            "Transaction hash must be a 66-character hexadecimal value."
        )

    transaction = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)

    print("\nTransaction summary")
    print("-------------------")
    print(f"Hash: {transaction['hash'].hex()}")
    print(f"From: {transaction['from']}")
    print(f"To: {transaction.get('to')}")
    print(f"Block: {transaction.get('blockNumber')}")
    print(f"Status: {receipt['status']}")
    print(f"Log count: {len(receipt['logs'])}")

    decoded_records = decode_event_logs(
        w3=w3,
        receipt=receipt,
        contract_abi=contract_abi,
    )

    return {
        "transaction": transaction,
        "receipt": receipt,
        "decoded_records": decoded_records,
    }


def fetch_tx_from_network(tx_hash, network_name):
    """
    Connect to the selected network and read a transaction.
    """

    print(f"Fetching {tx_hash} from {network_name}")

    w3 = get_web3_connection(network_name)

    print(f"Connected: {w3.is_connected()}")
    print(f"Current block: {w3.eth.block_number}")

    return read_transaction(
        w3=w3,
        tx_hash=tx_hash,
        contract_abi=GENERIC_EVENT_ABI,
    )


# -------------------------------------------------------------------
# COMMAND-LINE ENTRY POINT
# -------------------------------------------------------------------

def main():
    """
    Expected command:

    python scripts/tx-reader.py ethereum_mainnet 0xTRANSACTION_HASH
    """

    if len(sys.argv) < 3:
        script_name = sys.argv[0]

        print(
            "Usage:\n"
            f"  python {script_name} "
            "<network_name> <transaction_hash>\n\n"
            "Example:\n"
            f"  python {script_name} "
            "ethereum_mainnet 0xTRANSACTION_HASH"
        )

        sys.exit(1)

    network_name = sys.argv[1]
    tx_hash = sys.argv[2]

    try:
        fetch_tx_from_network(
            tx_hash=tx_hash,
            network_name=network_name,
        )
    except (
        ValueError,
        ConnectionError,
        OSError,
    ) as error:
        print(f"ERROR: {error}")
        sys.exit(1)
    except Exception as error:
        # Final boundary for unexpected RPC or web3.py errors.
        print(
            f"Unexpected transaction-reader error: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
