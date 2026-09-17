## New Break Categories

Blockchain introduces reconciliation breaks that do not commonly appear in traditional file-based or account-based reconciliation. These breaks arise because blockchain transactions have network fees, token-specific units, autonomous asset distributions, execution states, confirmation requirements, and pseudonymous address identifiers.

The following categories should be considered when designing an on-chain/off-chain reconciliation framework.

### 1. Gas Fee Discrepancies

Traditional payment and securities systems usually represent fees as explicit accounting entries. On blockchain networks, a transaction sender pays a network fee known as **gas**.

The gas fee is separate from the asset being transferred.

For example:

```text
Asset Transfer = 100 USDC
Network Fee = 0.001 ETH
```

The 100 USDC transfer may reconcile successfully while the related ETH gas expense remains unmatched.

A gas fee is generally determined using:

```text
Gas Fee = Gas Used × Effective Gas Price
```

The transaction receipt provides the actual gas consumed during execution. The effective gas price identifies the price paid for each unit of gas.

Common gas-related breaks include:

- The token movement is booked, but the gas expense is missing.
- The gas expense is assigned to the wrong wallet, legal entity, or cost center.
- The expected gas estimate is compared with the actual gas consumed.
- The native-asset fee is incorrectly combined with the token-transfer amount.
- The gas fee is converted into fiat using an inconsistent exchange rate or valuation timestamp.
- Several internal transactions are submitted through one blockchain transaction, but the gas expense is not allocated correctly.
- A failed transaction consumes gas even though the intended asset movement does not occur.

Gas should normally be treated as a separate reconciliation component:

```text
Business Asset Movement
+
Native-Asset Network Fee
=
Complete Economic Effect
```

#### Reconciliation Control

The reconciliation process should independently capture:

- Transaction hash
- Fee-paying address
- Gas used
- Effective gas price
- Native asset used for the fee
- Block timestamp
- Fiat valuation rate, if required
- Internal cost-center or account mapping

The token movement and gas expense should be matched separately, even when both originate from the same blockchain transaction.

---

### 2. Token Decimal Conversion Issues

ERC-20 event logs store token quantities as raw integers. The event log does not display the human-readable amount with a decimal point.

For example, a token transfer log might contain:

```text
raw_value = 1000000
```

The business meaning depends on the token's configured decimal precision.

If the token uses six decimals:

```text
1000000 ÷ 10^6 = 1 token
```

If the token uses eighteen decimals:

```text
1000000 ÷ 10^18 = 0.000000000001 token
```

The general conversion is:

```text
Human-Readable Amount = Raw Value ÷ 10^Token Decimals
```

This creates a major reconciliation risk because the same raw integer can represent very different economic quantities for different tokens.

Common decimal-related breaks include:

- The decoder assumes that every token uses eighteen decimals.
- Token decimals are missing from the reference-data repository.
- The incorrect contract address is used to retrieve token metadata.
- A proxy contract and implementation contract are confused.
- The raw integer is compared directly with the quantity in the off-chain ledger.
- Rounding rules differ between blockchain and accounting systems.
- A token's decimal configuration changes or is incorrectly maintained internally.
- The on-chain amount is correct, but the reconciliation engine manufactures a false break through incorrect normalization.

#### Reconciliation Control

Token reference data should include:

- Network
- Token contract address
- Token symbol
- Token name
- Decimal precision
- Internal asset identifier
- Effective date
- Approval or verification status

A normalized reconciliation record should preserve both values:

```python
record = {
    "raw_value": 1000000,
    "token_decimals": 6,
    "normalized_value": "1.000000"
}
```

Preserving the raw value supports auditability, while the normalized value supports comparison with the off-chain ledger.

---

### 3. Staking Rewards and Airdrops

Traditional financial systems often assume that an asset movement begins with a payment, trade, settlement, or transfer instruction.

Blockchain systems can generate asset movements without a corresponding instruction in the organization's transaction-processing platform.

Examples include:

- Staking rewards
- Validator rewards
- Protocol incentive payments
- Governance-token distributions
- Airdrops
- Rebasing adjustments
- Fee-sharing distributions
- Smart-contract reward claims

These events can increase an on-chain balance even when no matching trade or transfer instruction exists off-chain.

A reconciliation engine may initially classify the increase as:

```text
On-chain asset movement
+
No off-chain instruction
=
Unmatched break
```

However, the movement may be valid and require a different accounting classification.

Common reward- and airdrop-related breaks include:

- A wallet receives a token that is not present in the organization's asset master.
- An on-chain balance increases without an internal transaction reference.
- A reward is booked using the wrong income classification.
- The event is attributed to the wrong customer, fund, or legal entity.
- The asset has no approved valuation source.
- A received token is unsupported, restricted, or operationally unexpected.
- The same reward is recorded from both a balance change and an event log, creating a duplicate.
- An airdrop is incorrectly treated as an ordinary customer transfer.

#### Reconciliation Control

The process should distinguish between:

```text
Instruction-Driven Activity
```

and:

```text
Protocol-Generated or Unsolicited Activity
```

Exception handling should capture:

- Receiving wallet
- Token contract
- Raw and normalized quantity
- Distribution mechanism
- Transaction hash
- Block number and timestamp
- Internal ownership mapping
- Accounting classification
- Valuation status
- Review and approval status

The absence of an off-chain instruction should not cause the event to be silently discarded. It should create a visible and classifiable exception.

---

### 4. Failed-but-Mined Transactions

A blockchain transaction can be included in a block but fail during execution.

The transaction lifecycle may look like this:

```text
Transaction Submitted
↓
Transaction Included in a Block
↓
Smart-Contract Execution Reverts
↓
Transaction Receipt Status = Failed
```

This means the transaction exists on-chain, but the intended business operation did not complete.

For example, a user may attempt to transfer a token, but the smart contract may reject the transfer because:

- The wallet has an insufficient token balance.
- The sender has not provided the required allowance.
- A contract condition is not satisfied.
- The transaction exceeds a deadline.
- The contract is paused.
- Access-control rules reject the caller.
- Execution runs out of gas.

The transaction hash, block number, sender, gas consumption, and receipt still exist. However, the intended token transfer or contract state change does not occur.

Common failed-but-mined breaks include:

- The off-chain system treats transaction submission as settlement.
- An internal booking is created before the transaction receipt is checked.
- The transaction is found on-chain, but the reconciliation engine does not inspect its execution status.
- The expected event log is absent because execution reverted.
- The intended asset movement does not occur, but a gas expense is still incurred.
- Operations mistake transaction existence for successful business completion.

#### Reconciliation Control

The reconciliation process should separate three questions:

```text
1. Was the transaction submitted?
2. Was the transaction included in a block?
3. Did the intended business operation succeed?
```

A transaction should not be considered successfully settled solely because a transaction hash or block number exists.

The transaction receipt should be checked for:

- Execution status
- Gas used
- Expected event logs
- Contract address
- Block number
- Confirmation depth

A failed transaction may require two different outcomes:

```text
Expected Asset Movement = Not Settled
Gas Expense = Valid On-Chain Cost
```

---

### 5. Chain Reorganizations Before Finality

A chain reorganization, commonly called a **reorg**, occurs when a previously observed block is replaced by another block as the network determines its accepted chain history.

An application might initially observe:

```text
Block 100
└── Transaction A
```

After a reorganization, the accepted chain may become:

```text
Block 100
└── Transaction B
```

Transaction A may later appear in another block, return to a pending state, or disappear from the accepted chain.

This creates a reconciliation risk when an off-chain system treats the first observed block as immediately final.

Common reorganization-related breaks include:

- An event is booked off-chain before reaching the required confirmation depth.
- A previously processed event is removed from the accepted chain.
- The same transaction reappears with a different block number.
- A transaction is processed twice after being observed before and after a reorganization.
- The block timestamp or event sequence changes.
- The off-chain system reports settlement while the on-chain event is no longer canonical.
- Different participants apply different confirmation thresholds and therefore disagree about settlement status.

A transaction can pass through several operational states:

```text
Pending
↓
Included
↓
Provisionally Confirmed
↓
Operationally Accepted
↓
Final
```

The precise finality model depends on the blockchain network and the organization's control requirements.

#### Reconciliation Control

The reconciliation design should define:

- Required confirmation depth
- Conditions for provisional booking
- Conditions for final booking
- Reorganization detection logic
- Reversal or correction procedures
- Duplicate-processing protections
- Escalation thresholds for high-value transactions

An event-level record should use a durable identifier such as:

```text
Network + Transaction Hash + Log Index
```

The system should also retain the observed:

- Block number
- Block hash
- Confirmation count
- Processing status
- First-observed timestamp
- Finalized timestamp, when applicable

This allows the reconciliation process to detect when an event's block association changes.

For regulated or high-value settlement, all stakeholders should agree on the meaning of:

- Observed
- Confirmed
- Operationally settled
- Legally settled
- Final

The confirmation threshold should be treated as a formal control parameter rather than an informal technical setting.

---

### 6. Address Mapping Errors

Blockchain networks identify participants through addresses.

For example:

```text
0x28c6c06298d514db089934071355e5743bf21d60
```

The blockchain address does not inherently provide the internal business identity behind it.

Traditional systems usually identify ownership using:

- Customer IDs
- Account numbers
- Legal-entity identifiers
- Custody accounts
- Portfolio identifiers
- Product accounts
- Internal ledger codes

Reconciliation therefore depends on a controlled mapping between the blockchain address and the corresponding off-chain entity.

A simplified mapping might look like:

| Blockchain Field | Internal Reference |
|---|---|
| Network | Approved settlement network |
| Wallet address | Customer or custody account |
| Contract address | Token or asset identifier |
| `from` address | Source entity |
| `to` address | Destination entity |

Common address-mapping breaks include:

- A wallet address is missing from the reference-data repository.
- A wallet is mapped to the wrong customer or legal entity.
- Ownership changes but the internal mapping is not updated.
- Letter casing or normalization causes inconsistent comparisons.
- The same entity controls multiple addresses.
- Multiple customers are represented through an omnibus wallet.
- A smart-contract address is incorrectly treated as a customer wallet.
- An exchange deposit address is incorrectly treated as the ultimate beneficiary.
- A contract upgrade introduces a new address that is not present in the approved asset master.
- An unauthorized or unknown address interacts with a monitored asset.

Address mapping becomes particularly difficult when one blockchain address represents several underlying customer positions.

For example:

```text
Omnibus Wallet
├── Customer A = 40 tokens
├── Customer B = 35 tokens
└── Customer C = 25 tokens
```

The blockchain shows:

```text
Omnibus Wallet Balance = 100 tokens
```

The off-chain sub-ledger must explain how those 100 tokens are allocated among the underlying customers.

#### Reconciliation Control

The address reference-data model should include:

- Blockchain network
- Wallet or contract address
- Address type
- Customer or legal-entity mapping
- Internal account identifier
- Ownership model
- Effective-from date
- Effective-to date
- Approval status
- Custody classification
- Omnibus or segregated indicator

Addresses should be normalized consistently before comparison. For Ethereum-compatible networks, address handling should use the appropriate checksum-address validation.

The reconciliation process should distinguish among:

```text
Externally Owned Account
Smart-Contract Address
Token Contract
Custody Wallet
Exchange Wallet
Omnibus Wallet
Unknown Address
```

A technically valid on-chain transfer can still create a control break if the organization cannot determine which customer, account, or legal entity owns the sending or receiving address.

---

## New Break Categories — Control Summary

Each new break category affects a different part of the reconciliation framework:

| Break Category | Primary Reconciliation Risk | Key Control |
|---|---|---|
| Gas fee discrepancies | Incomplete economic accounting | Reconcile fees separately from asset movements |
| Token decimal conversion issues | Incorrect asset quantity | Maintain controlled token metadata and preserve raw values |
| Staking rewards and airdrops | Unexplained balance increases | Classify protocol-generated and unsolicited activity |
| Failed-but-mined transactions | False settlement recognition | Verify receipt status and expected event logs |
| Chain reorganizations before finality | Premature or reversed settlement | Apply confirmation and reorganization controls |
| Address mapping errors | Incorrect ownership attribution | Maintain governed wallet-to-entity reference data |

## Key Takeaway

Blockchain reconciliation must evaluate more than whether a transaction hash exists.

A complete control framework should determine:

1. Whether the transaction was included in the accepted chain.
2. Whether execution succeeded.
3. Whether the expected events were emitted.
4. Whether the transaction reached the required confirmation threshold.
5. Whether token quantities were normalized correctly.
6. Whether gas expenses were captured separately.
7. Whether all addresses were mapped to the correct off-chain entities.
8. Whether unsolicited or protocol-generated asset movements were classified.
9. Whether the event was processed exactly once.
10. Whether the resulting on-chain state agrees with the organization's off-chain books and records.

These controls convert raw blockchain activity into reconciliation evidence that operations, accounting, audit, compliance, and migration stakeholders can understand and trust.
