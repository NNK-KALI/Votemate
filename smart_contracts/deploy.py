import os
import json
from web3 import Web3
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Load bytecode
    # os.path.dirname(__file__) gives the dir where is the file is located
    with open(os.path.dirname(__file__) + "/" + "bytecode.json", "r") as file:
        bytecode = json.load(file)

    # Load ABI
    with open(os.path.dirname(__file__) + "/" + "ABI.json", "r") as file:
        abi = json.load(file)

    # Deploy to Ganache
    # we need web3 to connect to the ganache RPC

    # Connecting to Ganache
    # we need RPC, chain ID, account address,account private key
    web3 = Web3(Web3.HTTPProvider(os.environ["HTTP_PROVIDER"]))
    print(colored("smart contract deployed to blockchain.", "green"))
    # set default account to zero index
    web3.eth.default_account = web3.eth.accounts[
        int(os.environ["GANANCHE_ADMIN_ACCOUNT_INDEX"])
    ]

    # Create a Contract
    contest_contract = web3.eth.contract(abi=abi, bytecode=bytecode)

    # submit the transaction that deploys the contract
    tx_hash = contest_contract.constructor().transact()

    # Wait for the transaction to be mined, and get the transaction receipt
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # get contract address
    contract_address = tx_receipt.contractAddress

    # save contract address
    with open(
        os.path.dirname(__file__) + "/" + "deployed_contract_address.txt", "w"
    ) as file:
        file.write(contract_address)
