# ═══ R1 · LOAD CONFIG ══════════════════════════════════
# 1A Business Need .....: Connect to Ethereum without hardcoding secrets
# 1B Developer Question : Where does the node URL come from safely?
# 1C App Function ......: Reads the RPC URL from a local .env file
# 2  Capability ........: Environment configuration + command-line input
# 3  Library ...........: os, sys, python-dotenv, web3.py
# 4  Import ............: from dotenv import load_dotenv / from web3 import Web3
# 5  Implementation ....: load_dotenv(); os.getenv("WEB3_PROVIDER_URL")
import os
import sys
from dotenv import load_dotenv
from web3 import Web3

# → reads .env into environment variables (keeps the URL out of git)
load_dotenv()
# → pulls the node URL; returns None if .env doesn't have it
RPC_URL = os.getenv("WEB3_PROVIDER_URL")

# ═══ R2 · DEFINE CHAIN FINALITY THRESHOLD ═══════════════════
# 1A Business Need .....: Agree on when a tx is technically irreversible
# 1B Developer Question : How many blocks on top is "final" for us?
# 1C App Function ......: One shared depth every check uses
# 2  Capability ........: Named constant
# 3  Library ...........: native Python
# 4  Import ............: —
# 5  Implementation ....: CONFIRMATION_DEPTH = 12
# → a risk decision, not a universal rule; same value as yesterday's is_confirmed()
CONFIRMATION_DEPTH = 12

# ═══ R3 · CHECK CHAIN FINALITY (TECHNICAL) ══════════════════
# 1A Business Need .....: Know whether the ledger itself can still change
# 1B Developer Question : Is this tx buried deep enough to be irreversible?
# 1C App Function ......: Compares current chain tip to the tx's block
# 2  Capability ........: Read chain state + arithmetic
# 3  Library ...........: web3.py
# 4  Import ............: from web3 import Web3
# 5  Implementation ....: w3.eth.block_number - block_number >= depth
def is_chain_final(w3, block_number, depth=CONFIRMATION_DEPTH):
    # → latest block height right now, minus our block = confirmations
    confirmations = w3.eth.block_number - block_number
    # → True only once buried at least `depth` blocks deep
    return confirmations >= depth

# ═══ R4 · CHECK SETTLEMENT FINALITY (LEGAL / OPERATIONAL) ═════════
# 1A Business Need .....: Only book a tx as SETTLED when ALL conditions hold
# 1B Developer Question : What besides the chain decides "settled"?
# 1C App Function ......: Layers off-chain conditions on top of chain finality
# 2  Capability ........: Ordered conditional logic (a decision ladder)
# 3  Library ...........: native Python
# 4  Import ............: —
# 5  Implementation ....: if/return chain -> recon -> compliance, in that order
def settlement_status(chain_final, recon_matched, compliance_ok):
    # → gate 1: if the chain itself isn't final, nothing else matters yet
    if not chain_final:
        return "PENDING - not yet chain-final"
    # → gate 2: chain-final but the books don't agree = open recon break
    if not recon_matched:
        return "CHAIN-FINAL, NOT SETTLED - recon break open"
    # → gate 3: books agree but compliance hasn't signed off
    if not compliance_ok:
        return "CHAIN-FINAL, NOT SETTLED - awaiting compliance sign-off"
    # → only reached when every gate passed
    return "SETTLED - chain-final AND all off-chain conditions met"

# ═══ R5 · RUN AGAINST A REAL TRANSACTION ═════════════════════
# 1A Business Need .....: Prove chain-final does NOT automatically mean settled
# 1B Developer Question : Same tx, different off-chain states - what changes?
# 1C App Function ......: Runs one real tx through three simulated off-chain states
# 2  Capability ........: Script entry point + loop over test scenarios
# 3  Library ...........: native Python + web3.py
# 4  Import ............: (already imported above)
# 5  Implementation ....: if __name__ == "__main__": ... for recon, comp in [...]
if __name__ == "__main__":
    # → connect to the node using the URL loaded in R1
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    # → fetch the tx whose hash you typed after the script name
    tx = w3.eth.get_transaction(sys.argv[1])
    # → the ONE technical answer: is it final on-chain?
    chain_final = is_chain_final(w3, tx["blockNumber"])
    print(f"Chain-final at depth {CONFIRMATION_DEPTH}? {chain_final}\n")
    # → simulated off-chain flags; in real life these come from your recon engine + compliance system
    for recon, comp in [(False, False), (True, False), (True, True)]:
        # → same tx, three different settlement answers
        print(f"recon={recon}, compliance={comp} -> {settlement_status(chain_final, recon, comp)}")
