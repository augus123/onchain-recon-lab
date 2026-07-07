# 01 — On-Chain / Off-Chain Reconciliation Primer

   Setting the stage: what reconciliation has always been, and what actually
   changes when one side of the rec becomes a shared, public ledger.

   ## 1. Traditional Reconciliation

   - **The core control:** independently prove that two sets of books agree — internal ledgers vs. an external source of truth (custodian, bank, exchange, counterparty) — across cash, positions, and transactions.
   - **Batch-driven by design:** end-of-day statements and files (SWIFT MT940/950 cash, MT535/536 positions, CSV/XML extracts) are loaded into a matching engine on a daily cycle with hard cut-offs.
   - **Rule-based matching:** auto-match on key fields (amount, value date, reference, account, ISIN); everything unmatched becomes an exception — a "break."
   - **Break management is the real work:** investigate, classify (timing vs. true difference), assign ownership, age, escalate, resolve — all with an auditable trail.
   - **Timing noise dominates:** settlement lags (T+1/T+2), cut-off windows, and time zones mean many breaks self-heal; the skill is separating noise from genuine risk (misbookings, fails, fraud).
   - **A regulatory control, not housekeeping:** completeness, frequency, and sign-off are evidenced for audit and regulation (SOX, client asset rules, operational risk frameworks).
   - **The trust model:** every party keeps its own ledger and no single record is authoritative — reconciliation itself is how "truth" gets established.

   ## 2. Why Blockchain Changes It

   - **One side of the rec becomes shared:** all parties can read the same chain state, so "my books vs. your books" collapses into "my books vs. the chain" — the external statement is now a queryable, cryptographically verifiable dataset.
   - **Reconciliation doesn't disappear — it relocates:** internal (off-chain) records — sub-ledgers, customer balances, wallet-to-account mappings, accounting entries — still have to be proven against on-chain reality.
   - **New break categories appear:** gas fees as unplanned cash movements, token decimal/unit conversions, staking rewards and airdrops with no initiating instruction, failed-but-mined transactions, reorgs before finality.
   - **Settlement semantics change:** contractual settlement dates give way to block confirmations and finality; atomic DvP-style settlement removes classic fails, while address errors become irreversible.
   - **The batch day dies:** a 24/7/365 ledger has no end-of-day — "as-of" snapshots at a block height and continuous monitoring replace the overnight cycle.
   - **Reference data becomes the control point:** the chain shows addresses, not customers — wallet-to-entity mapping (especially omnibus structures) is the new critical static data.
   - **Evidence gets stronger:** instead of trusting a statement, you can independently re-derive balances from raw chain data — which is exactly where forensic analysis begins.
