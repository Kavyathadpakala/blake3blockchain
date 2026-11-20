from .benchmark import run_benchmark, run_tamper_demo, generate_transactions
from .blockchain import Blockchain

def sample_demo(algorithm):
    chain = Blockchain(algorithm)
    chain.add_transactions_in_blocks(generate_transactions(5), block_size=2)
    print(f"\\nBlockchain using {algorithm.upper()}")
    for block in chain.chain:
        print(f"\\nBlock #{block.index} | transactions: {len(block.transactions)}")
        print("Previous hash:", block.previous_hash)
        print("Block hash   :", block.block_hash)
        for tx in block.transactions:
            print(f"  T{tx.tx_id}: {tx.sender} -> {tx.receiver}, amount={tx.amount}, hash={tx.tx_hash[:16]}...")
    print("\\nVerification:", chain.verify_chain())

def main():
    while True:
        print("\\n========== BLAKE3 BLOCKCHAIN - PHASE 1 ==========")
        print("1. Build sample blockchain using SHA-256")
        print("2. Build sample blockchain using sequential BLAKE3")
        print("3. Compare 1,000 / 5,000 / 10,000 / 50,000 transaction blockchains")
        print("4. Demonstrate transaction tamper detection")
        print("5. Exit")
        choice = input("Enter choice (1-5): ").strip()
        if choice == "1":
            sample_demo("sha256")
        elif choice == "2":
            sample_demo("blake3")
        elif choice == "3":
            run_benchmark()
        elif choice == "4":
            run_tamper_demo()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
