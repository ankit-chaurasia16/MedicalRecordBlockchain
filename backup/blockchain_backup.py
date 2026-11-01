import json
import hashlib
from pathlib import Path
from web3 import Web3

RPC_URL = "http://127.0.0.1:8545"
DEPLOYMENT_FILE = Path(__file__).parent / "deployed_contract.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_contract():
    if not w3.is_connected():
        raise ConnectionError("Local blockchain is not running.")

    if not DEPLOYMENT_FILE.exists():
        raise FileNotFoundError("deployed_contract.json not found. Deploy contract first.")

    with open(DEPLOYMENT_FILE, "r", encoding="utf-8") as file:
        deployment = json.load(file)

    address = Web3.to_checksum_address(deployment["contract_address"])

    contract = w3.eth.contract(
        address=address,
        abi=deployment["abi"]
    )

    return contract


def calculate_record_hash(record_data):
    serialized_data = json.dumps(
        record_data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )

    return hashlib.sha256(
        serialized_data.encode("utf-8")
    ).hexdigest()


def store_hash_on_blockchain(record_id, hash_hex):
    contract = get_contract()

    hash_bytes = bytes.fromhex(hash_hex)
    account = w3.eth.accounts[0]

    transaction = contract.functions.storeRecordHash(
        int(record_id),
        hash_bytes
    ).transact({
        "from": account
    })

    receipt = w3.eth.wait_for_transaction_receipt(transaction)

    if receipt["status"] != 1:
        raise Exception("Blockchain transaction failed.")

    return receipt["transactionHash"].hex()


def verify_hash_on_blockchain(record_id, hash_hex):
    contract = get_contract()

    hash_bytes = bytes.fromhex(hash_hex)

    result = contract.functions.verifyRecordHash(
        int(record_id),
        hash_bytes
    ).call()

    return result
