import json
from web3 import Web3, exceptions
from termcolor import colored
import os
from dotenv import load_dotenv

load_dotenv()


class Contest:
    def __init__(self, connect_to_blockchain=False) -> None:
        if connect_to_blockchain:
            # Load ABI
            with open(os.path.dirname(__file__) + "/" + "ABI.json", "r") as file:
                abi = json.load(file)

            # load deployed contract address
            with open(
                os.path.dirname(__file__) + "/" + "deployed_contract_address.txt", "r"
            ) as file:
                contract_address = file.read()

            # connnecting to blockchain(Ganache)
            web3 = Web3(Web3.HTTPProvider(os.environ["HTTP_PROVIDER"]))

            if web3.isConnected():
                print(colored(f"connected to {os.environ['HTTP_PROVIDER']}.", "green"))

            # set default account to index
            web3.eth.default_account = web3.eth.accounts[
                int(os.environ["GANANCHE_ADMIN_ACCOUNT_INDEX"])
            ]

            # make a connection to the deployed contract
            # This is used to interact with the contract
            self.contest = web3.eth.contract(
                address=contract_address,
                abi=abi,
            )

            # check if connection was successful
            if (
                self.contest.address.lower() == contract_address.lower()
                and self.contest.abi == abi
            ):
                print(colored("Connected to contract successfully!", "green"))
            else:
                print(colored("Failed to connect to contract.", "red"))

            # Instance of web3 to interact with the connected blockchain.
            # In this case Ganache is the provider.
            # We need this to achive some functionality like to wait until
            # we get the transaction receipt using wait_for_transaction_receipt()
            # eg: tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            self.w3 = Web3(self.contest.web3.provider)

    def get_contract_address(self):
        """
        Get the address where the contract is deployed.
        """
        return self.contest.address

    def add_contestant(self, name, party, age, qualification):
        """
        Add the contestant
        """
        try:
            tx_hash = self.contest.functions.addContestant(
                name, party, age, qualification
            ).transact()
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            tx_report = {
                "status": True,
                "tx_receipt": tx_receipt,
            }
        except exceptions.ValidationError as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        except Exception as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        finally:
            return tx_report

    def get_contestants_count(self):
        """
        Get the count of no:of participating contestants
        """
        return self.contest.functions.contestantsCount().call()

    def get_contestants(self):
        """
        Get the list of the participating contestants
        The contestants are stored in mappings(uint => Contestant)
        So, we need to iterate over the id's to get the contestant details.
        Note: The Contestant.id starts from 1.
        """
        contestants_list = []
        for i in range(1, self.get_contestants_count() + 1):
            contestant = self.contest.functions.contestants(i).call()
            contestant_details = {
                "id": contestant[0],
                "name": contestant[1],
                "voteCount": contestant[2],
                "party": contestant[3],
                "age": contestant[4],
                "qualification": contestant[5],
            }
            contestants_list.append(contestant_details)
        return contestants_list

    def get_current_phase(self):
        """
        Get current phase
        """
        phases = {0: "registration", 1: "voting", 2: "results"}
        state = self.contest.functions.state().call()
        phase = phases[state]
        return phase

    def set_phase(self, state):
        """
        Change state
        The available option for setting a phase are:
        1. 'register' for registration phase
        2. 'voting' for voting phase
        3. 'result' for post voting phase(result phase)
        """
        phases = {"registration": 0, "voting": 1, "results": 2}
        phase = phases[state]
        try:
            # Send transaction
            tx_hash = self.contest.functions.changeState(phase).transact()
            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            tx_report = {
                "status": True,
                "tx_receipt": tx_receipt,
            }
        except exceptions.SolidityError as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        except Exception as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        finally:
            return tx_report

    def voter_registration(self, voter_public_key):
        """
        To register the voter the admin needs to send it to the
        blockchain and set the isRegistered to true.
        """
        try:
            # Send the transaction
            tx_hash = self.contest.functions.voterRegistration(
                voter_public_key
            ).transact()
            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            tx_report = {
                "status": True,
                "tx_receipt": tx_receipt,
            }
        except exceptions.ValidationError as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        except Exception as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        finally:
            return tx_report

    def vote(self, contestant_id, voter_private_key):
        """
        Note: Do not prepend '0x' for voters private key.
        example format: 'c42c46db............................................bf'

        We need to use the user's account to sign this transaction and send the transaction.
        so, We need to get the voter's private key and contestant id ( The contestant
        whom he want to vote ).
        """
        # Convert the private key to account object. so that we can use this for making transactions
        voter_account = self.w3.eth.account.privateKeyToAccount(voter_private_key)

        try:
            # Send the signed transaction
            tx_hash = self.contest.functions.vote(contestant_id).transact(
                {"from": voter_account.address}
            )
            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            tx_report = {
                "status": True,
                "tx_receipt": tx_receipt,
            }
        except exceptions.SolidityError as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        except Exception as e:
            print(colored(e, "red"))
            tx_report = {
                "status": False,
                "tx_receipt": None,
            }
        finally:
            return tx_report

    def get_voters_count(self):
        """
        Get voters count
        """
        return self.contest.functions.votersCount().call()

    def get_voters(self):
        """
        Get voters list with their address and properties
        """
        voters_list = []
        for i in range(self.get_voters_count()):
            # The voters are stored as mapping(address => Voter).
            # so, we need to iterate over the address.
            # Inorder to get the details of the voter we need to pass the address
            # to the voters mapping(basically mapping is like hashtables and uses
            # the address as key to access the voter).
            # The addresses are stored in an array called votersAddresses.
            # so, first we need to get the address from the array using index and
            # use that address as key for the mapping to get voter details.

            voter_address = self.contest.functions.votersAddresses(i).call()
            voter = self.contest.functions.voters(voter_address).call()
            voter_details = {
                "address": voter_address,
                "hasVoted": voter[0],
                "vote": voter[1],
                "isRegistered": voter[2],
            }
            voters_list.append(voter_details)
        return voters_list

    def get_winner_ids(self):
        """
        Get the winner Id.
        """
        contestants_votes = []
        for i in range(1, self.get_contestants_count() + 1):
            contestant = self.contest.functions.contestants(i).call()
            contestants_votes.append({"id": contestant[0], "voteCount": contestant[2]})
        max_vote_count = max([c["voteCount"] for c in contestants_votes])
        winners = [
            c["id"] for c in contestants_votes if c["voteCount"] == max_vote_count
        ]
        if len(winners) == 1:
            return winners  # single winner
        else:
            return winners  # multiple winners

    def get_votes_count(self):
        """
        Get votes count.
        """
        return self.contest.functions.votesCount().call()

    def private_key_to_account_address(self, private_key):
        """
        Helper function to convert the private_key to account address.
        """
        try:
            account = self.w3.eth.account.privateKeyToAccount(private_key)
            return account.address
        except Exception as e:
            print(colored(e, "red"))
            return None
