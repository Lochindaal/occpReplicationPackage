import os
from enum import Enum

from protocol.utils.config_utils import load_config
from protocol.utils.thread_utils import write_thread_safe


class DataType(Enum):
    WORKLOAD = 1
    VOTE = 2
    REPLAY = 3
    STMTS = 4


class DataWriterHelper:

    def __init__(self, run_args):
        self.config = load_config()
        self.result_path = os.path.join(self.config["DATA"]["ResultBaseDir"], self.config["DATA"]["OccpResultDir"])
        self.result_file = os.path.join(self.result_path, "worker_results.json")
        self.run_args = run_args

    def write_data(self, worker_id: int, data_type: int, data_value, worker_type):
        value_name = "Time"
        if DataType(data_type) == DataType.STMTS:
            value_name = "Statements"

        run_key = f"{self.run_args['key']}_{self.run_args['scenario'].name}_{self.run_args['steps']}_{self.run_args['run_id']}"
        data = {"key": run_key,
                "Type": DataType(data_type).name, value_name: data_value,
                "Worker": {"Id": worker_id, "Type": worker_type}}
        write_thread_safe(data, self.result_file)
