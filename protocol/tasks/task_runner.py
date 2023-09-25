import pickle

from mona.interpreter.environment.environment import Environment
from mona.interpreter.parsing.parser import Parser

from protocol.storage.data_storage import DataStorage


class TaskRunner:
    def __init__(self, workload):
        self.workload = workload
        task_id = workload["taskId"]
        trace_id = workload["traceId"]
        code = workload["code"]
        trace = workload["traceLocation"]

        self.taskId = task_id
        self.traceId = trace_id
        self.storage = DataStorage("ecs")
        self.code = pickle.loads(self.load_trace_from_storage(code))
        self.startEnv: Environment = pickle.loads(self.load_trace_from_storage(trace))

    def load_trace_from_storage(self, storage_key):
        return self.storage.load(storage_key)

    def run(self, dump_dir="resources/dump_dir"):
        program, cmp_store = Parser.parse(self.code)
        cur_env: Environment = self.startEnv
        cur_env._exec_mode._dump_dir = dump_dir
        cur_env.before_execution()
        program.eval(cur_env)
        cur_env.after_execution()
