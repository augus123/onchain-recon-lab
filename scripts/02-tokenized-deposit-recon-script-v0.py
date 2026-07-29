import json

def fetch_mock_tokenized_deposit():
    """
    Simulates fetching a transaction record that includes both 
    on-chain (blockchain) and off-chain (fiat) statuses.
    """
    # This mock JSON represents a bank's liability on a blockchain [6]
    transaction_json = '''
    {
        "tx_id": "0x9876543210abcdef...",
        "asset": "Tokenized Deposit - USD",
        "amount": 50000.00,
        "on_chain_status": "confirmed",
        "confirmations": 32,
        "off_chain_settlement_status": "pending",
        "fiat_rail": "RTP/CHIPS",
        "timestamp": "2026-07-24T09:00:00Z"
    }
    '''
    return json.loads(transaction_json)
  def reconcile_finality_states(tx):
    """
    Parses the transaction and flags discrepancies between 
    on-chain confirmation and off-chain settlement.
    """
    tx_id = tx.get("tx_id")
    on_chain = tx.get("on_chain_status")
    off_chain = tx.get("off_chain_settlement_status")
    
    print(f"--- Reconciling Transaction: {tx_id} ---")
    print(f"Current On-Chain Status: {on_chain}")
    print(f"Current Off-Chain Status: {off_chain}")

    # Core logic to identify a reconciliation break [8]
    if on_chain == "confirmed" and off_chain == "pending":
        print("[!] ALERT: RECONCILIATION BREAK DETECTED")
        print("REASON: The transaction has achieved technical blockchain finality, "
              "but legal settlement finality on traditional rails (RTP/CHIPS) "
              "is still pending [6, 7].")
        return "BREAK"
    
    elif on_chain == "confirmed" and off_chain == "settled":
        print("[+] SUCCESS: Books are aligned. Both technical and legal finality achieved.")
        return "ALIGNED"
    
    else:
        print("[...] INFO: Transaction is still in progress across hybrid environments.")
        return "IN_PROGRESS"
      if __name__ == "__main__":
    # Simulate fetching the transaction [4]
    mock_tx = fetch_mock_tokenized_deposit()
    
    # Run the reconciliation check [8]
    result = reconcile_finality_states(mock_tx)
    
    print(f"Final Audit Result: {result}")
