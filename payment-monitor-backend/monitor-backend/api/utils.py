import web3.exceptions
from web3 import Web3
#from web3.logs import IGNORE
import json


def get_erc20_transaction_details(tx_id):
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com/"))
    glm_token_address = "0x0B220b82F3eA3B7F6d9A1D8ab58930C064A2b5Bf"
    ERC20ABI = [{"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"}, {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [
        {"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name":"decimals", "outputs":[{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name":"name", "outputs":[{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name":"symbol", "outputs":[{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name":"totalSupply", "outputs":[{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}]
    token_contract = w3.eth.contract(address=glm_token_address, abi=ERC20ABI)
    transfer_info = {}
    try:
        transaction_info = w3.eth.getTransaction(tx_id)
        transfer_info['transaction_found'] = True
    except web3.exceptions.TransactionNotFound:
        transfer_info['transaction_found'] = False
        return transfer_info

    if transaction_info.to.lower() != token_contract.address.lower():
        raise Exception(
            f"Seems like transaction is not with expected token: {transaction_info.to} vs {token_contract.address}")

    # both transaction info and transaction receipt are needed to get full transaction data
    try:
        transaction_receipt = w3.eth.getTransactionReceipt(tx_id)
        transfer_info['transaction_receipt_found'] = True
    except web3.exceptions.TransactionNotFound:
        transfer_info['transaction_receipt_found'] = False
        return transfer_info

    if transaction_receipt["status"] != 1:
        raise Exception(f"Transaction receipt status not equal to 1: {tx_id}")

    try:
        logs = token_contract.events.Transfer().processReceipt(
            transaction_receipt, web3.logs.IGNORE)
        transfer_info['failure_to_process'] = False
    except Exception as ex:
        transfer_info['failure_to_process'] = True
        return transfer_info

    for log in logs:
        if "event" in log and log.event == "Transfer":
            transfer_info["from"] = log["args"]["from"]
            transfer_info["to"] = log["args"]["to"]
            transfer_info["value"] = log["args"]["value"]
            # Human value is for tokens with 18 decimals, like GLM. It's human read-able (but it's loosing precision)
            transfer_info["human_value"] = transfer_info["value"] / 1.0E18
            transfer_info["gas_used"] = transaction_receipt["gasUsed"]
            transfer_info["gas_price"] = transaction_receipt["effectiveGasPrice"]
            transfer_info["gas_price_gwei"] = transaction_receipt["effectiveGasPrice"] / 1.0E9
            # Human-readable gas cost in Gwei.
            transfer_info["human_gas_cost"] = transfer_info["gas_used"] * \
                transfer_info["gas_price"] / 1.0E18

    if transfer_info:
        return transfer_info

    print(f"Failed to get transaction info due to uknown problem: {tx_id}")
    return None
