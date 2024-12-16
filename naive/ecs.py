import hashlib
import json
import logging

from protocol.utils.config_utils import load_config
from protocol.utils.thread_utils import write_thread_safe
from protocol.utils.web3_utils import Web3ProviderType, init_web3_connection
from web3.middleware import geth_poa_middleware


def load_abi(contract_description):
    with open(contract_description) as f:
        info_json = json.load(f)
    return info_json["abi"]


def create_task_json(task_data):
    code, target = task_data
    return {
        "taskId": 0,
        "code": code,
        "expectedResult": target,
    }


def get_hash(value):
    return hashlib.sha256(value.encode()).digest()


class ExecutionCertificationSystemNaive:
    def __init__(self, contract_address, description_file, network, account, run_args):
        self.contractAddress = contract_address
        self.abi = load_abi(description_file)
        self.w3 = init_web3_connection(Web3ProviderType.HTTP, network)
        self.private_key = (
            "0x758f3576e39c3503d2d139e27ce171e282cc70b40c60d1356456f3a4f1575a57"
        )
        self.run_args = run_args
        self.transaction_log_file = "./data/results/occp/transaction_log.json"
        # inject poa middleware (needed for L2)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.account = account
        self.chain = self.w3.eth.chain_id
        self.contract = self.w3.eth.contract(address=contract_address, abi=self.abi)
        with open("./data/ecs/wallets.json", "r") as json_file:
            self.accounts = json.load(json_file)
        self.logger = logging.getLogger(load_config()["LOGGING"]["LogName"])

    def get_workload_seq(self, worker_id=0):
        account = self.accounts[worker_id]["acc"]
        pk = self.accounts[worker_id]["pk"]
        tx_data = self.contract.functions.getWorkloadSeq()
        receipt, _ = self.send_transaction(tx_data, account, pk)
        self.logger.info(
            f"Transaction Cost: {receipt.gasUsed} ['get_workload_seq', worker: {worker_id}]"
        )
        self.log_gas_usage(receipt, "get_workload_seq")
        return self.extract_workload(receipt)

    def extract_workload(self, receipt):
        logs = self.contract.events["WorkloadGet"]().process_receipt(receipt)
        return logs[0]["args"]["workload"]

    def get_tasks(self):
        # ToDo: rewrite to use transaction?
        return self.contract.functions.getTasks().call()

    def get_vote_threshold(self):
        return self.contract.functions.getVoteThreshold().call()

    def set_vote_threshold(self, threshold):
        tx_data = self.contract.functions.setVoteThreshold(threshold)
        receipt, _ = self.send_transaction(tx_data)
        self.logger.info(f"Transaction Cost: {receipt.gasUsed} ['set_vote_threshold']")
        self.log_gas_usage(receipt, "set_vote_threshold")

    def add_task_seq(self, task_data):
        tx_data = self.contract.functions.addTask(create_task_json(task_data))
        receipt, _ = self.send_transaction(tx_data)
        self.logger.info(f"Transaction Cost: {receipt.gasUsed} ['add_task_seq']")
        tasks = self.get_tasks()
        task_id = tasks[len(tasks) - 1][0]
        self.log_gas_usage(receipt, "add_task_seq")
        return task_id

    def send_transaction(self, tx_data, account=None, pk=None):
        nonce = self.w3.eth.get_transaction_count(self.account)
        if account is None:
            dynamic_fee_transaction = {
                "nonce": nonce,
                "from": self.account,
                "gasPrice": 1,
                "gas": 200000000,
            }
        else:
            nonce = self.w3.eth.get_transaction_count(account)
            dynamic_fee_transaction = {
                "nonce": nonce,
                "from": account,
                "gasPrice": 1,
                "gas": 20000000,
            }
        tx = tx_data.build_transaction(dynamic_fee_transaction)
        if pk is None:
            signed_tx = self.w3.eth.account.sign_transaction(
                tx, private_key=self.private_key
            )
        else:
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=pk)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, 180)

        return receipt, tx_hash

    def vote(self, task_id: int, result: bool, acc_idx):
        account = self.accounts[acc_idx]["acc"]
        pk = self.accounts[acc_idx]["pk"]
        tx_data = self.contract.functions.vote(task_id, result)
        receipt, tx_hash = self.send_transaction(tx_data, account, pk)
        self.logger.info(
            f"Transaction Cost: {receipt.gasUsed} ['vote', taskId: {task_id}, accIdx: {acc_idx}]"
        )

        self.log_gas_usage(receipt, "vote")
        return receipt, tx_hash

    def get_certificate(self, task_id):
        return self.contract.functions.getCert(task_id).call()

    # Helper Functions (not used in code)
    def get_certificates(self):
        return self.contract.functions.getCertificates().call()

    def log_gas_usage(self, receipt, func_name):
        run_id = self.run_args["run_id"]
        run_key = f"{self.run_args['key']}_{self.run_args['scenario'].name}_{self.run_args['steps']}_{run_id}"
        data = {"key": run_key, "function": func_name, "gasUsed": receipt.gasUsed}
        write_thread_safe(data, self.transaction_log_file)
