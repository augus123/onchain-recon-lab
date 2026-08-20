import sys
from web3 import Web3

INFURA_URL = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

TRANSFER_SELECTOR = "0xa9059cbb"
TRANSFER_EVENT_SIG = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

contract = w3.eth.contract(abi=ERC20_ABI)


def decode_transfer_input(input_data):
    input_data = input_data.hex() if not isinstance(input_data, str) else input_data
    if not input_data.startswith("0x"):
        input_data = "0x" + input_data

    if not input_data.startswith(TRANSFER_SELECTOR):
        print("Not a standard ERC-20 transfer call.")
        return None

    func_obj, func_params = contract.decode_function_input(input_data)
    to_address = func_params["_to"]
    value = func_params["_value"]
    print(f"Requested transfer -> to: {to_address}, value: {value}")
    return {"to": to_address, "value": value}


def decode_transfer_log(receipt):
    for log in receipt["logs"]:
        topics = [t.hex() if not isinstance(t, str) else t for t in log["topics"]]
        topics = [t if t.startswith("0x") else "0x" + t for t in topics]

        if topics[0] == TRANSFER_EVENT_SIG:
            sender = w3.to_checksum_address("0x" + topics[1][-40:])
            receiver = w3.to_checksum_address("0x" + topics[2][-40:])
            value = int(log["data"], 16)
            print(f"Actual on-chain transfer -> from: {sender}, to: {receiver}, value: {value}")
            return {"from": sender, "to": receiver, "value": value}
    print("No Transfer event found in logs.")
    return None


def decode_tx(tx_hash):
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)

    requested = decode_transfer_input(tx["input"])
    actual = decode_transfer_log(receipt)

    if requested and actual:
        if requested["value"] == actual["value"]:
            print("MATCH: requested value equals on-chain event value. Transfer reconciled.")
        else:
            print("MISMATCH: requested value does not equal on-chain event value. Flag for review.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tx-reader.py <transaction_hash>")
        sys.exit(1)

    if not w3.is_connected():
        print("Failed to connect to Ethereum node.")
        sys.exit(1)

    decode_tx(sys.argv[1])


--Audit & Edge Cases

--Run this 10,000 times against real mainnet traffic, here's where it breaks or misleads you:

--Non-standard transfer paths — Router contracts, transferFrom, smart-contract wallets, or tokens with a nonstandard ABI won't match the plain transfer(address,uint256) selector. The script will report "not a standard ERC-20 transfer" even though a real transfer happened — a false negative on your reconciliation.
--Multiple Transfer events in one transaction — DEX swaps and batch payments often emit several Transfer logs in a single tx. decode_transfer_log() grabs the first match and stops, silently ignoring the rest. You'd think you reconciled the whole transaction when you only checked one leg of it.
--No RPC error handling — If Infura times out or rate-limits (easy to hit on the free tier), the script just crashes on that call instead of logging it and moving on. At scale, one flaky network blip kills the whole batch run instead of just that one transaction.
