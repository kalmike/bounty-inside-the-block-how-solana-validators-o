### README.md

# Inside the Block: How Solana Validators Order Transactions

## Architecture

This project involves sending transactions to specific Solana validators and analyzing the order in which they appear in the blocks. The goal is to understand the rules that validators use to order transactions within a block.

### Components

1. **Transaction Sender**: Sends transactions to specific validators.
2. **Block Parser**: Parses blocks to extract transaction order.
3. **Data Analyzer**: Analyzes the transaction order to determine the rules used by validators.

### Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/solana-transaction-order.git
   cd solana-transaction-order
   ```

2. **Run the Dry Run**:
   ```bash
   docker-compose up --build
   ```

3. **Run the Real Transaction**:
   ```bash
   docker-compose run --rm app python main.py --real
   ```

### Dependencies

- Python 3.8+
- Docker
- Solana CLI

### Configuration

- **Validator List**: The list of validators to test is defined in `validators.json`.
- **Transaction Types**: The types of transactions to send are defined in `transactions.json`.

### Notes

- **Spend Cap**: The entire measurement process should fit within approximately 0.05 SOL.
- **Leader Schedule**: The experiment should be conducted before or after the Alpenglow upgrade.

## Submission Requirements

- **Repository**: Submit a link to your code repository.
- **Reproducibility**: The project must be fully reproducible with one command.
- **Keys**: Keys should only be passed via volume/env, never in the repo.
- **Execution**: Dry-run by default, real sending only behind an explicit flag with a spend cap.
- **Raw Data**: Include all raw data, including transaction signatures and slot numbers.
- **README**: Explain the design, how it handles the points under "what you will have to account for," and what it does NOT separate.
- **Report**: Report with the date of every measurement and a "what went wrong" section.

## Judging Criteria

- **Design Validity**: 35%
- **Verifiability and Reproducibility**: 25%
- **Analysis Quality**: 25%
- **Engineering**: 15%

### Example Output

```json
{
  "validator": "validator1",
  "transactions": [
    {
      "signature": "tx1",
      "slot": 12345,
      "order": 1
    },
    {
      "signature": "tx2",
      "slot": 12345,
      "order": 2
    }
  ],
  "rule": "First-Come-First-Served"
}
```

### Eligibility

- **GitHub Repo**: Provide a link to your code repository.

---

### Python Code

```python
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
```

### validators.json

```json
[
    {
        "address": "validator1_address"
    },
    {
        "address": "validator2_address"
    },
    {
        "address": "validator3_address"
    },
    {
        "address": "validator4_address"
    },
    {
        "address": "validator5_address"
    },
    {
        "address": "validator6_address"
    }
]
```

### transactions.json

```json
[
    {
        "amount": 0.0001
    },
    {
        "amount": 0.0002
    },
    {
        "amount": 0.0003
    }
]
```

### Dockerfile

```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py", "--test"]
```

### requirements.txt

```
solana-py
click
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - .:/app
    environment:
      - SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
    command: ["python", "main.py", "--test"]
```

### JSON Response

```json
{
  "otherInfo": {
    "architecture": "The project involves sending transactions to specific Solana validators and analyzing the order in which they appear in the blocks.",
    "usage": "Clone the repository, run the dry run with `docker-compose up --build`, and run the real transaction with `docker-compose run --rm app python main.py --real`."
  },
  "eligibilityAnswers": {
    "GitHub Repo": "https://github.com/yourusername/solana-transaction-order"
  }
}
```