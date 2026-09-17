# 01 — On-Chain / Off-Chain Reconciliation Primer

Setting the stage: what reconciliation has always been, and what actually changes when one side of the reconciliation becomes a shared, public ledger.

---

# 1. Traditional Reconciliation

## Core Concepts

- **The core control:** Independently prove that two sets of books agree: internal ledgers versus an external source of truth such as custodians, banks, exchanges, or counterparties.
- **Batch-driven by design:** End-of-day statements and files (SWIFT MT940/950 cash statements, MT535/536 positions, CSV/XML extracts) are loaded into matching engines on scheduled cycles.
- **Rule-based matching:** Matches are performed using fields such as amount, value date, reference number, account, and ISIN.
- **Break management is the real work:** Analysts investigate, classify, assign, escalate, and resolve unmatched items.
- **Timing noise dominates:** Settlement lags, cut-off windows, and time zone differences cause many breaks that later self-resolve.
- **A regulatory control, not housekeeping:** Reconciliation supports auditability, operational risk controls, and regulatory compliance.
- **The trust model:** Each participant maintains its own ledger; reconciliation establishes operational truth.

## Key Takeaway

Traditional reconciliation exists because multiple organizations maintain separate books and records.

---

# 2. Why Blockchain Changes Reconciliation

## What Changes

- One side of the reconciliation becomes shared.
- All participants can independently query blockchain state.
- Internal books still require validation against on-chain records.
- Settlement finality becomes more important than settlement date.
- Continuous monitoring replaces end-of-day processing cycles.
- Wallet-to-customer mapping becomes critical reference data.

## New Break Categories

- Gas fee discrepancies
- Token decimal conversion issues
- Staking rewards and airdrops
- Failed-but-mined transactions
- Chain reorganizations before finality
- Address mapping errors

## Key Takeaway

Blockchain does not eliminate reconciliation.

Traditional model:

```text
Internal Books ↔ External Books
```

Blockchain model:

```text
Internal Books ↔ Blockchain State
```

---

# 3. Initial Thoughts on the Reconciliation Workstream

Establishing a robust reconciliation framework is the architectural backbone of any blockchain migration.

It bridges the gap between:

- Legacy ledger finality
- Blockchain settlement finality
- Tokenized asset movement
- Off-chain accounting systems

Success requires alignment between:

- Technology teams
- Operations teams
- Compliance functions
- Control owners

The reconciliation engine should be treated as a foundational design component rather than a post-migration audit tool.

Benefits include:

- Reduced operational risk
- Improved data integrity
- Stronger auditability
- Better migration readiness
- Enhanced regulatory compliance

---

# 4. Reconciling Tokenized Assets

The ability to reliably decode ERC-20 transfers across diverse transaction patterns is foundational for modern reconciliation programs.

Robust decoding enables:

- Independent verification of asset movements
- Automated break detection
- Regulatory reporting
- Audit trail generation
- Ledger-to-ledger validation

This capability becomes especially important for:

- Stablecoins
- Tokenized deposits
- Tokenized securities
- Settlement tokens

Many token transfers involve:

- Zero native ETH movement
- Smart contract interactions
- Internal contract calls
- Multi-step settlement workflows

The real business movement often exists only within event logs.

---

# 5. Why Decoding Robustness Is the Control

In traditional reconciliation systems, file formats are contractually fixed.

Examples:

- FIX
- SWIFT
- CSV
- XML

A malformed file typically causes the entire feed to fail.

Blockchain creates a different risk model.

A decoder can fail silently while still producing plausible-looking results.

This is often more dangerous than a hard failure.

---

## Failure Mode #1: Same Event, Multiple Shapes

A transfer may appear as:

- Simple wallet-to-wallet transfer
- `transferFrom()` call
- DEX swap
- Internal smart-contract transfer
- Batched multicall
- Proxy token transfer

A decoder that handles only the simplest case may silently ignore real production volume.

---

## Failure Mode #2: Event Identity Problems

Similar events may exist across multiple token standards.

Examples:

- ERC-20 Transfer
- ERC-721 Transfer
- ERC-1155 Transfer

A naive decoder may:

- Misclassify events
- Assign incorrect amounts
- Produce false matches

The result is often a believable but incorrect reconciliation record.

---

## Failure Mode #3: Decimal Handling

Blockchain logs store raw integers.

Examples:

```text
USDC = 6 decimals
Most ERC-20 tokens = 18 decimals
```

Incorrect decimal resolution can create:

- False breaks
- False matches
- Material reporting errors

Example:

```text
1,000,000 USDC
```

may decode incorrectly if token decimals are not applied properly.

---

## Operational Impact

### False Positives and False Negatives

Operations teams begin ignoring exception queues filled with noise.

### Parallel Run Risk

Migration programs rely on proving old and new systems agree on 100% of transaction volume.

### Regulatory Reporting Risk

Incomplete event decoding leads to incomplete audit populations.

---

# 6. Reconciliation Challenges in Hybrid Environments

Tokenized deposits and tokenized assets create a hybrid operating model:

```text
Blockchain Networks
+
Traditional Banking Systems
```

Both environments must remain synchronized.

---

## Challenge 1: Reconciling Different Finality Models

### Blockchain Finality

Blockchain transactions become increasingly irreversible after confirmation and consensus.

### Legal Settlement Finality

Regulatory and contractual settlement rules may define final ownership differently.

### Reconciliation Impact

A transaction can be:

- Technically final on-chain
- Not yet legally settled off-chain

This creates reconciliation complexity.

---

## Challenge 2: Traditional Payment Rail Integration

Examples:

- RTP
- CHIPS
- SWIFT

Challenges include:

- Data transformation
- Timing differences
- Different operating schedules
- Parallel ledger maintenance

Blockchain operates continuously.

Traditional banking systems often do not.

---

## Challenge 3: Auditability

Blockchain provides:

- Immutable records
- Transparent transaction histories
- Independent verification

Traditional systems provide:

- Legal ownership records
- Accounting books
- Customer statements

Reconciliation must prove consistency across both environments.

---

## Enhanced Hybrid Scope

Tokenization expands reconciliation beyond traditional settlement processing.

Organizations must now manage:

- Multiple sources of truth
- Blockchain event streams
- Traditional ledger records
- Cross-platform exception management
- New operational controls

This significantly increases:

- Governance complexity
- Testing effort
- Monitoring requirements
- Stakeholder coordination

---

# 7. The Blockchain Reconciliation Paradigm

Blockchain does not eliminate reconciliation.

Instead, it changes what must be reconciled and where reconciliation breaks occur.

## What Blockchain Solves

Blockchain simplifies proving:

- Did the transaction occur?
- Which block contains it?
- Did execution succeed?
- Which contract processed it?
- Which events were emitted?

Because blockchain data is:

- Shared
- Immutable
- Cryptographically verifiable

Organizations no longer need to compare multiple blockchain ledgers to establish transaction existence.

---

## What Blockchain Does NOT Solve

Blockchain cannot prove:

- The transaction booked correctly in internal systems.
- Customer mappings are accurate.
- Accounting entries were created correctly.
- Regulatory reporting is complete.

The problem shifts from:

```text
Ledger vs Ledger
```

to:

```text
On-Chain Event vs Off-Chain Business Record
```

---

## Mapping On-Chain Events to Business Records

### On-Chain Data

- Contract address
- Sender address
- Recipient address
- Raw amount
- Transaction hash
- Block number
- Log index

### Off-Chain Data

- Journal ID
- Account ID
- Asset identifier
- Settlement reference
- Processing status
- Booking timestamp

### Typical Mapping Model

| On-Chain Field | Off-Chain Equivalent |
|--------------|----------------------|
| Transaction Hash | Settlement Reference |
| Contract Address | Asset Identifier |
| from | Source Account |
| to | Destination Account |
| Raw Value | Ledger Quantity |
| Block Timestamp | Booking Timestamp |
| Log Index | Event Identifier |

---

## Common Blockchain Reconciliation Breaks

### On-Chain Event Not Recorded Off-Chain

Transfer exists on-chain but missing from internal systems.

### Off-Chain Event Missing On-Chain

Business event recorded internally but not found on-chain.

### Amount Mismatch

Incorrect decimal conversion.

### Address Mapping Error

Wallet not mapped correctly to internal customer records.

### Status Mismatch

Internal systems report settled while blockchain reports failed or pending.

### Duplicate Processing

Same blockchain event processed multiple times.

### Timing Differences

Events land in different reconciliation windows.

---

# 8. Event Logs as Reconciliation Data Sources

Event logs are often the most important reconciliation data source.

Transaction-level data rarely provides enough business context.

---

## ERC-20 Transfer Event

```solidity
event Transfer(
    address indexed from,
    address indexed to,
    uint256 value
);
```

### Key Reconciliation Fields

- from
- to
- value

Example decoded record:

```python
record = {
    "event_name": "Transfer",
    "tx_hash": transaction_hash,
    "log_index": log_index,
    "block_number": block_number,
    "block_time_utc": block_time,
    "contract_address": token_contract,
    "from": sender_address,
    "to": recipient_address,
    "raw_value": token_value
}
```

---

## Why Event Logs Matter

Traditional environments rely on:

- SWIFT messages
- Position statements
- CSV extracts

Blockchain systems rely on:

- Event logs
- ABI definitions
- Topic hashes
- Smart contract state changes

---

## Event-Level Keys

Transaction hashes alone are insufficient.

A stronger unique identifier is:

```text
Network +
Transaction Hash +
Log Index
```

One transaction may emit multiple events.

---

# 9. Smart Contracts and Automated Controls

Smart contracts automate business rules such as:

- Escrow
- Atomic swaps
- Delivery-versus-payment (DvP)
- Asset settlement

These controls reduce certain reconciliation risks.

However, they do not eliminate reconciliation requirements.

---

## Smart Contract Break Conditions

Examples include:

- Reverted transaction
- Missing event emission
- Unexpected event emission
- Unauthorized transfers
- Stuck contract state
- Insufficient confirmations

---

## State-Based Reconciliation

Example asset lifecycle:

```text
Issued
↓
Transferred
↓
Locked
↓
Settled
↓
Redeemed
```

Each transition should be validated
