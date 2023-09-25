import copy
import hashlib
import json
import pickle

import eth_abi
from hexbytes import HexBytes
from web3.middleware import geth_poa_middleware

from protocol.utils.web3_utils import init_web3_connection, Web3ProviderType


def prepare_traces(snapshots, trace_storage_location, malicious_user=False):
    traces = []
    sequence_hashes = []
    for i in range(len(snapshots) - 1):
        snap_dict_start = copy.deepcopy(snapshots[i]).__dict__
        snap_id = snap_dict_start["_exec_mode"]._snap_id
        del snap_dict_start["_exec_mode"]
        sequence_hashes.append(hashlib.sha256(pickle.dumps(snap_dict_start)).digest())
        traces.append(
            {
                "traceId": snap_id + 1,  # ToDo make traceId random but unique and within range of max snapshots!
                "traceLocation": str(trace_storage_location[i]),
                "startTraceHash": hashlib.sha256(pickle.dumps(snap_dict_start)).digest(),
            }
        )
    last_snap = copy.deepcopy(snapshots[len(snapshots) - 1]).__dict__
    del last_snap["_exec_mode"]
    if malicious_user:
        sequence_hashes.append(hashlib.sha256("5".encode()).digest())
    else:
        sequence_hashes.append(hashlib.sha256(pickle.dumps(last_snap)).digest())
    return traces, sequence_hashes


def load_abi(contract_description):
    with open(contract_description) as f:
        info_json = json.load(f)
    return info_json["abi"]


def create_task_json(task_data):
    code, traces, target_sequence, _, open_traces = task_data
    return {
        "taskId": 0,
        "code": code,
        "traces": traces,
        "targetSequence": target_sequence,
    }


def get_hash(value):
    return hashlib.sha256(value.encode()).digest()


class ExecutionCertificationSystem:
    def __init__(self, contract_address, description_file, network, account):
        self.contractAddress = contract_address
        self.abi = load_abi(description_file)
        self.w3 = init_web3_connection(
            Web3ProviderType.HTTP, network
        )  # self.load_w3_provider(network)
        self.private_key = (
            "0x758f3576e39c3503d2d139e27ce171e282cc70b40c60d1356456f3a4f1575a57"
        )
        # inject poa middleware (needed for L2)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.account = account
        self.chain = self.w3.eth.chain_id
        self.contract = self.w3.eth.contract(address=contract_address, abi=self.abi)
        with open("./data/ecs/wallets.json", "r") as json_file:
            self.accounts = json.load(json_file)

    def get_workload(self):
        return self.contract.functions.getWorkload().call()

    def get_workload_seq(self, worker_id=0):
        account = self.accounts[worker_id]["acc"]
        pk = self.accounts[worker_id]["pk"]
        tx_data = self.contract.functions.getWorkloadSeq()
        receipt, tx_hash = self.send_transaction(tx_data, account, pk)
        return self.extract_workload(receipt)

    def extract_workload(self, receipt):
        logs = self.contract.events["WorkloadGet"]().process_receipt(receipt)
        return logs[0]["args"]["workload"]

    def get_tasks(self):
        return self.contract.functions.getTasks().call()

    def add_task_seq(self, task_data):
        tx_data = self.contract.functions.addTask(create_task_json(task_data))
        self.send_transaction(tx_data)
        tasks = self.get_tasks()
        task_id = tasks[len(tasks) - 1][0]
        return task_id

    def send_transaction(self, tx_data, account=None, pk=None):
        nonce = self.w3.eth.get_transaction_count(self.account)
        if account is None:
            dynamic_fee_transaction = {
                "nonce": nonce,
                "from": self.account,
                "gasPrice": 2000000000,
            }
        else:
            nonce = self.w3.eth.get_transaction_count(account)
            dynamic_fee_transaction = {
                "nonce": nonce,
                "from": account,
                "gasPrice": 2000000000,
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

    def add_traces(self, task_id, traces):
        tx_data = self.contract.functions.addTraces(task_id, traces)
        self.send_transaction(tx_data)

    def get_sequence_data(self, task_id: int):
        return self.contract.functions.getTaskSequence(task_id).call()

    def upload_conflicts(self, task_id: int, conflicts, acc_idx=0):
        account = self.accounts[acc_idx]["acc"]
        pk = self.accounts[acc_idx]["pk"]
        hex_sequences = [HexBytes(x).hex() for x in conflicts]
        tx_data = self.contract.functions.uploadConflicts(task_id, hex_sequences)
        return self.send_transaction(tx_data, account, pk)

    def upload_sequence(self, task_id, sequence, acc_idx=0):
        account = self.accounts[acc_idx]["acc"]
        pk = self.accounts[acc_idx]["pk"]
        sequence_string = "".join([str(x) for x in sequence])
        hex_sequences = [HexBytes(x).hex() for x in sequence]
        tx_data = self.contract.functions.uploadPossibleSequence(
            task_id, hex_sequences, sequence_string
        )
        return self.send_transaction(tx_data, account, pk)

    def vote(self, task_id: int, trace_id: int, target_hash, acc_idx):
        account = self.accounts[acc_idx]["acc"]
        pk = self.accounts[acc_idx]["pk"]
        tx_data = self.contract.functions.vote(task_id, trace_id, target_hash)
        return self.send_transaction(tx_data, account, pk)

    def get_certificate(self, code, start, target):
        concat = eth_abi.packed.encode_packed(
            ["bytes32", "bytes32", "bytes32"], [get_hash(code), start, target]
        )
        cert_h = hashlib.sha256(concat).digest()
        return self.contract.functions.getCertificate(cert_h).call()

    # Helper Functions (not used in code)
    def get_certificates(self):
        return self.contract.functions.getCertificates().call()
