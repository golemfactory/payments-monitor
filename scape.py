import web3.exceptions
from web3 import Web3
#from web3.logs import IGNORE
import json

def get_erc20_transaction_details(token_contract, tx_id):
    transfer_info = {}
    try:
        transaction_info = w3.eth.getTransaction(tx_id)
    except web3.exceptions.TransactionNotFound:
        raise Exception(f"Transaction not found on chain: {tx_id}")

    if transaction_info.to.lower() != token_contract.address.lower():
        raise Exception(f"Seems like transaction is not with expected token: {transaction_info.to} vs {token_contract.address}")

    try:
        transaction_receipt = w3.eth.getTransactionReceipt(tx_id)
    except web3.exceptions.TransactionNotFound:
        raise Exception(f"Transaction receipt not found on chain: {tx_id}")

    if transaction_receipt["status"] != 1:
        raise Exception(f"Transaction receipt status not equal to 1: {tx_id}")

    try:
        logs = token_contract.events.Transfer().processReceipt(transaction_receipt, web3.logs.IGNORE)
    except Exception as ex:
        raise Exception(f"Failed to process receipt {tx_id}: {ex}")

    for log in logs:
        if "event" in log and log.event == "Transfer":
            transfer_info["from"] = log["args"]["from"]
            transfer_info["to"] = log["args"]["to"]
            transfer_info["value"] = log["args"]["value"]
            transfer_info["human_value"] = transfer_info["value"] / 1.0E18
            transfer_info["gas_used"] = transaction_receipt["gasUsed"]
            transfer_info["gas_price"] = transaction_receipt["effectiveGasPrice"]
            transfer_info["gas_price_gwei"] = transaction_receipt["effectiveGasPrice"] / 1.0E9
            transfer_info["human_gas_cost"] = transfer_info["gas_used"] * transfer_info["gas_price"] / 1.0E18

    if transfer_info:
        print(f"Transaction parsed successfully: {transfer_info}")
        return transfer_info

    print(f"Failed to get transaction info due to uknown problem: {tx_id}")
    return None


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com/"))
    glm_token_address = "0x0B220b82F3eA3B7F6d9A1D8ab58930C064A2b5Bf"
    with open("IERC20.abi.json", "r") as abi_file:
        erc20abi = json.loads(abi_file.read())
    glm_contract = w3.eth.contract(address=glm_token_address, abi=erc20abi)
    get_erc20_transaction_details(glm_contract, "0x1ac8a969f318f85086c8ed7ea66c8314d1f730570833f1d4336cd1abaadc314d")
    get_erc20_transaction_details(glm_contract, "0x1ac8a969f318f85086c8ed7ea66c8314d1f730570833f1d4336cd1abaadc314d")
