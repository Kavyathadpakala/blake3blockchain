import json, time, csv
from dataclasses import dataclass
from pathlib import Path
from .hashing import hash_bytes

@dataclass
class StoredTransaction:
    tx_id: int
    sender: str
    receiver: str
    amount: float
    nonce: int
    tx_hash: str

    def content_bytes(self):
        data = {"tx_id": self.tx_id, "sender": self.sender, "receiver": self.receiver,
                "amount": self.amount, "nonce": self.nonce}
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list
    previous_hash: str
    algorithm: str
    block_hash: str = ""

    def header_bytes(self):
        data = {"index": self.index, "timestamp": self.timestamp,
                "transaction_hashes": [tx.tx_hash for tx in self.transactions],
                "previous_hash": self.previous_hash, "algorithm": self.algorithm}
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def calculate_hash(self):
        return hash_bytes(self.header_bytes(), self.algorithm)

class Blockchain:
    def __init__(self, algorithm):
        if algorithm not in ("sha256", "blake3"):
            raise ValueError("Algorithm must be sha256 or blake3.")
        self.algorithm = algorithm
        self.chain = []
        genesis = Block(0, time.time(), [], "0" * 64, algorithm)
        genesis.block_hash = genesis.calculate_hash()
        self.chain.append(genesis)

    def add_transactions_in_blocks(self, transactions, block_size=100):
        if block_size <= 0:
            raise ValueError("Block size must be positive.")
        for start in range(0, len(transactions), block_size):
            batch = transactions[start:start + block_size]
            stored = []
            for tx in batch:
                stored.append(StoredTransaction(
                    tx.tx_id, tx.sender, tx.receiver, tx.amount, tx.nonce,
                    hash_bytes(tx.to_bytes(), self.algorithm)))
            previous = self.chain[-1]
            block = Block(len(self.chain), time.time(), stored,
                          previous.block_hash, self.algorithm)
            block.block_hash = block.calculate_hash()
            self.chain.append(block)

    def verify_chain(self):
        for i, block in enumerate(self.chain):
            for tx in block.transactions:
                if hash_bytes(tx.content_bytes(), self.algorithm) != tx.tx_hash:
                    return False, f"Block {i}: transaction {tx.tx_id} hash mismatch."
            if block.calculate_hash() != block.block_hash:
                return False, f"Block {i}: block hash mismatch."
            if i and block.previous_hash != self.chain[i-1].block_hash:
                return False, f"Block {i}: previous hash link mismatch."
        return True, "All transaction hashes, block hashes, and chain links are valid."

    def export_csv(self, output_dir):
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / f"{self.algorithm}_transactions.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["block_index","transaction_id","sender","receiver","amount","nonce","transaction_hash"])
            for block in self.chain:
                for tx in block.transactions:
                    w.writerow([block.index,tx.tx_id,tx.sender,tx.receiver,tx.amount,tx.nonce,tx.tx_hash])
        with (out / f"{self.algorithm}_blocks.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["block_index","transaction_count","previous_hash","block_hash","algorithm"])
            for b in self.chain:
                w.writerow([b.index,len(b.transactions),b.previous_hash,b.block_hash,b.algorithm])
