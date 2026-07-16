from web3 import Web3

# 1. Connect
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/6840803ddb334ee384c2bcdb51832da6'))

# Minimal ABI for decoding transfer(address,uint256)
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

def decode_tx(tx_hash):
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    
    # --- Input Data Decoding ---
    contract = w3.eth.contract(abi=ERC20_ABI)
    try:
        func_obj, func_params = contract.decode_function_input(tx['input'])
        print(f"\n--- Input Data ---")
        print(f"Function: {func_obj.fn_name}")
        print(f"To: {func_params['_to']}, Value: {func_params['_value']}")
    except ValueError:
        print("\nInput data does not match standard ERC-20 transfer signature.")

    # --- Event Log Decoding ---
    # Using the contract interface to decode events is much cleaner
    # For a real implementation, you'd load the full standard ERC-20 ABI
    print(f"\n--- Event Logs ---")
    for log in receipt['logs']:
        # Check if this is a Transfer event by topic
        if log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
            # This is the Transfer event
            print(f"Token Address: {log['address']}")
            print(f"From: {'0x' + log['topics'][1].hex()[-40:]}")
            print(f"To: {'0x' + log['topics'][2].hex()[-40:]}")
            print(f"Value: {int(log['data'].hex(), 16)}")

# Run for your hash
decode_tx('0xc320223c521d61846e2353e8113c996215bcd798ccced104bdcabb40f4f6acfe')