from web3 import Web3

# 1. Connect to an Ethereum Node
w3 = Web3(Web3.HTTPProvider('YOUR_INFURA_OR_ALCHEMY_API_URL'))

tx_hash = 'YOUR_SELECTED_TX_HASH'

# 2. Fetch Transaction and Receipt
tx = w3.eth.get_transaction(tx_hash)
receipt = w3.eth.get_transaction_receipt(tx_hash)

# 3. Inspect Input for transfer() signature (a9059cbb)
print(f"Input Data Signature: {tx['input'][:10]}")

# 4. Decode Event Logs
# Use the ERC-20 Transfer Event Signature: 
# 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
transfer_event_signature = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

for log in receipt['logs']:
    if log['topics'][0].hex() == transfer_event_signature:
        sender = '0x' + log['topics'][1].hex()[-40:]
        receiver = '0x' + log['topics'][2].hex()[-40:]
        value = int(log['data'].hex(), 16)
        print(f"Token: {log['address']}, From: {sender}, To: {receiver}, Amount: {value}")
