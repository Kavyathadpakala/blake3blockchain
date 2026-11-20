UPDATED PHASE 1 - BLOCKCHAIN BLAKE3
===================================

This project:
- Generates deterministic sample payment transactions.
- Uses the same transaction records for SHA-256 and sequential BLAKE3.
- Stores actual transactions in blocks of 100.
- Computes one hash per transaction and one hash per block.
- Verifies transaction hashes, block hashes and previous-block links.
- Benchmarks 1,000, 5,000, 10,000 and 50,000 transactions.
- Repeats timings five times and reports medians.
- Exports CSV data and graphs.

SETUP (Windows PowerShell, from this folder):
  py -m venv .venv
  .venv\Scripts\Activate.ps1
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  python -m src.main

If activation is blocked:
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .venv\Scripts\Activate.ps1

MENU:
1 SHA-256 sample blockchain
2 Sequential BLAKE3 sample blockchain
3 Full comparison for all four dataset sizes
4 Tamper detection
5 Exit

RESULTS FOLDER:
- transactions_1000.csv, transactions_5000.csv, transactions_10000.csv,
  transactions_50000.csv: input transaction datasets.
- comparison_results.csv: benchmark results.
- sha256_transactions.csv and blake3_transactions.csv: block assignment and
  transaction hashes for the final 50,000-transaction experiment.
- sha256_blocks.csv and blake3_blocks.csv: block summaries for final experiment.
- blockchain_creation_time.png, verification_time.png,
  throughput_comparison.png, blake3_speedup.png.

LIMITATIONS:
This is a local research prototype. It does not yet implement PoS consensus,
digital signatures, account balance validation, networking, or parallel
processing. Those are future extensions. TPS here means local transaction
hashing/block-building throughput, not distributed network TPS.
