import json
import requests
import time
from solana.rpc.api import Client
from solana.transaction import Transaction, TransactionInstruction
from solana.publickey import PublicKey
from solana.system_program import transfer
from solana.keypair import Keypair

# Configuration
VALIDATORS = json.load(open('validators.json'))
TRANSACTIONS = json.load(open('transactions.json'))
SOLANA_RPC_URL = 'https://api.mainnet-beta.solana.com'
SOLANA_FEE = 0.000001  # 1 lamport per transaction

# Initialize Solana client
client = Client(SOLANA_RPC_URL)

# Keypair for sending transactions
sender_keypair = Keypair.generate()

def send_transaction(to_address, amount):
    tx = Transaction()
    tx.add(transfer(sender_keypair.public_key, PublicKey(to_address), amount * 10**6))
    tx.fee_payer = sender_keypair.public_key
    tx.sign(sender_keypair)
    return client.send_transaction(tx)

def get_block(slot):
    return client.get_block(slot)

def analyze_block(block):
    transactions = block['transactions']
    ordered_transactions = sorted(transactions, key=lambda x: x['transaction']['message']['account_keys'][0])
    return ordered_transactions

def main(real=False):
    results = []
    for validator in VALIDATORS:
        validator_address = validator['address']
        for transaction in TRANSACTIONS:
            if real:
                print(f"Sending transaction to {validator_address}")
                tx_signature = send_transaction(validator_address, transaction['amount'])
                print(f"Transaction sent with signature: {tx_signature}")
                time.sleep(5)  # Wait for transaction to be confirmed
            slot = client.get_latest_blockhash()['result']['last_valid_slot']
            block = get_block(slot)
            ordered_transactions = analyze_block(block)
            results.append({
                'validator': validator_address,
                'transactions': ordered_transactions,
                'rule': 'Unknown'  # Placeholder for rule analysis
            })
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Solana Transaction Order Analysis')
    parser.add_argument('--test', action='store_true', help='Run dry run')
    parser.add_argument('--real', action='store_true', help='Run real transaction')
    args = parser.parse_args()

    if args.test:
        print("Running dry run...")
        results = main(real=False)
        print(json.dumps(results, indent=2))
    elif args.real:
        print("Running real transaction...")
        results = main(real=True)
        print(json.dumps(results, indent=2))
    else:
        print("Please specify --test or --real")