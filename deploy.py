import json
import os
from web3 import Web3

RPC_URL = "http://127.0.0.1:8545"
ARTIFACT_PATH = os.path.join(
    "artifacts",
    "contracts",
    "MedicalRecords.sol",
    "MedicalRecords.json"
)

print("Connecting to local blockchain...")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("Blockchain not connected. Start 'npx hardhat node' first.")

print("Blockchain connected!")
print("Chain ID:", w3.eth.chain_id)

if not os.path.exists(ARTIFACT_PATH):
    raise FileNotFoundError("Contract artifact not found. Run npx hardhat compile.")

with open(ARTIFACT_PATH, "r") as file:
    artifact = json.load(file)

abi = artifact["abi"]
bytecode = artifact["bytecode"]

account = w3.eth.accounts[0]
print("Deploying from account:", account)

contract_factory = w3.eth.contract(
    abi=abi,
    bytecode=bytecode
)

transaction_hash = contract_factory.constructor().transact({
    "from": account
})

print("Deployment transaction sent...")
receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)

contract_address = receipt["contractAddress"]

deployment_info = {
    "contract_address": contract_address,
    "abi": abi
}

with open("deployed_contract.json", "w") as file:
    json.dump(deployment_info, file, indent=4)

print("\nCONTRACT DEPLOYED SUCCESSFULLY!")
print("Contract Address:", contract_address)
print("Transaction Hash:", receipt["transactionHash"].hex())
print("Saved details in deployed_contract.json")
