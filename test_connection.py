from database import get_connection
from blockchain import get_contract, w3

print("===== MYSQL CONNECTION TEST =====")

connection = get_connection()
cursor = connection.cursor()

cursor.execute("SHOW TABLES")
print("Tables:", cursor.fetchall())

cursor.close()
connection.close()

print("\n===== BLOCKCHAIN CONNECTION TEST =====")

print("Connected:", w3.is_connected())

contract = get_contract()

print("Contract address:", contract.address)
print("Contract owner:", contract.functions.owner().call())

print("\nALL CONNECTION TESTS PASSED!")
