import csv, random, statistics, time
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import psutil
from .transaction import Transaction
from .blockchain import Blockchain

COUNTS = [1000, 5000, 10000, 50000]
BLOCK_SIZE = 100
REPEATS = 5

def generate_transactions(count):
    rng = random.Random(2026)
    wallets = [f"wallet_{i:05d}" for i in range(1, 2001)]
    result = []
    for i in range(1, count + 1):
        sender = rng.choice(wallets)
        receiver = rng.choice(wallets)
        while receiver == sender:
            receiver = rng.choice(wallets)
        result.append(Transaction(i, sender, receiver, round(rng.uniform(1, 10000), 2), i))
    return result

def save_input(transactions, path):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["transaction_id","sender","receiver","amount","nonce"])
        for t in transactions:
            w.writerow([t.tx_id,t.sender,t.receiver,t.amount,t.nonce])

def one_run(algorithm, transactions):
    chain = Blockchain(algorithm)
    start = time.perf_counter()
    chain.add_transactions_in_blocks(transactions, BLOCK_SIZE)
    build_time = time.perf_counter() - start
    start = time.perf_counter()
    valid, message = chain.verify_chain()
    verify_time = time.perf_counter() - start
    if not valid:
        raise RuntimeError(message)
    return chain, build_time, verify_time

def measure(algorithm, transactions):
    builds, verifies, last_chain = [], [], None
    for _ in range(REPEATS):
        last_chain, b, v = one_run(algorithm, transactions)
        builds.append(b)
        verifies.append(v)
    return last_chain, statistics.median(builds), statistics.median(verifies)

def make_graphs(rows, out):
    x = [r["transactions"] for r in rows]
    graphs = [
        ("blockchain_creation_time.png", "Blockchain creation time (seconds)",
         "Blockchain creation time comparison", "sha256_build_seconds", "blake3_build_seconds"),
        ("verification_time.png", "Verification time (seconds)",
         "Blockchain verification time comparison", "sha256_verify_seconds", "blake3_verify_seconds"),
        ("throughput_comparison.png", "Transactions hashed per second",
         "Hashing/build throughput comparison", "sha256_tps", "blake3_tps"),
    ]
    for filename, ylabel, title, a, b in graphs:
        plt.figure()
        plt.plot(x, [r[a] for r in rows], marker="o", label="SHA-256")
        plt.plot(x, [r[b] for r in rows], marker="o", label="BLAKE3")
        plt.xlabel("Number of transactions")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(out / filename, dpi=160)
        plt.close()
    plt.figure()
    plt.plot(x, [r["speedup"] for r in rows], marker="o")
    plt.axhline(1, linestyle="--")
    plt.xlabel("Number of transactions")
    plt.ylabel("SHA-256 build time / BLAKE3 build time")
    plt.title("BLAKE3 speedup relative to SHA-256")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out / "blake3_speedup.png", dpi=160)
    plt.close()

def run_benchmark():
    out = Path("results")
    out.mkdir(exist_ok=True)
    rows = []
    print("\nBLOCKCHAIN-BASED SEQUENTIAL HASHING COMPARISON")
    print(f"Block size: {BLOCK_SIZE}; repetitions: {REPEATS}")
    print("Both algorithms use exactly the same transaction records.")
    print("-" * 105)
    print(f"{'Count':>9} {'SHA build':>12} {'BLAKE3 build':>14} {'SHA verify':>12} {'BLAKE3 verify':>15} {'SHA TPS':>12} {'BLAKE3 TPS':>12}")
    process = psutil.Process()
    for count in COUNTS:
        transactions = generate_transactions(count)
        save_input(transactions, out / f"transactions_{count}.csv")
        sha_chain, sb, sv = measure("sha256", transactions)
        blake_chain, bb, bv = measure("blake3", transactions)
        sha_chain.export_csv(out)
        blake_chain.export_csv(out)
        stps = count / sb if sb else 0
        btps = count / bb if bb else 0
        rows.append({
            "transactions": count, "block_size": BLOCK_SIZE,
            "blocks_excluding_genesis": (count + BLOCK_SIZE - 1)//BLOCK_SIZE,
            "sha256_build_seconds": sb, "blake3_build_seconds": bb,
            "sha256_verify_seconds": sv, "blake3_verify_seconds": bv,
            "sha256_tps": stps, "blake3_tps": btps,
            "speedup": sb/bb if bb else 0,
            "blake3_improvement_percent": ((sb-bb)/sb*100) if sb else 0,
            "memory_usage_mb_after_run": process.memory_info().rss/(1024*1024)
        })
        print(f"{count:>9} {sb:>12.6f} {bb:>14.6f} {sv:>12.6f} {bv:>15.6f} {stps:>12.2f} {btps:>12.2f}")
    with (out / "comparison_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    make_graphs(rows, out)
    print("\nCompleted. Every generated chain passed verification.")
    print("See results/ for CSV files and graphs.")
    print("TPS is local transaction hashing/build throughput, not network TPS.")

def run_tamper_demo():
    chain = Blockchain("blake3")
    chain.add_transactions_in_blocks(generate_transactions(5), 100)
    print("Before tampering:", chain.verify_chain())
    chain.chain[1].transactions[0].amount += 999
    print("After tampering :", chain.verify_chain())
