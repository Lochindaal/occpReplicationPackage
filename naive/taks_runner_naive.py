import pickle
import io
import contextlib
import sys
import threading

from mona.interpreter.environment.environment import (
    Environment,
    ExecModeRecord,
    ExecModeRun,
)
from mona.interpreter.parsing.parser import Parser
from protocol.storage.data_storage import DataStorage

stdout_lock = threading.Lock()


class TaskRunnerNaive:
    def __init__(self, workload):
        self.workload = workload
        task_id = workload["taskId"]
        code = workload["code"]

        self.taskId = task_id
        self.code = code
        self.result = None

    def run3(self, dump_dir="resources/dump_dir"):
        original_stdout = sys.stdout  # Keep track of original stdout
        thread_stdout = io.StringIO()  # Thread-specific buffer
        program, cmp_store = Parser.parse(self.code)
        exec_mode = ExecModeRecord(dump_dir=dump_dir, steps=100000000000)
        cur_env = Environment(exec_mode=exec_mode)

        try:
            sys.stdout = thread_stdout  # Redirect stdout to this thread’s buffer

            cur_env.before_execution()
            program.eval(cur_env)
            cur_env.after_execution()

            expected_res = thread_stdout.getvalue()
            res = list(filter(None, expected_res.split("\n")))

            if len(res) > 0:
                self.result = res[-1]
            else:
                self.result = "ERROR!"

        finally:
            sys.stdout = original_stdout

    def run(self, dump_dir="resources/dump_dir"):
        program, cmp_store = Parser.parse(self.code)
        exec_mode = ExecModeRecord(dump_dir=dump_dir, steps=100000000000)
        # exec_mode = ExecModeRun(dump_dir=dump_dir)
        cur_env = Environment(exec_mode=exec_mode)
        # captured_output = io.StringIO()
        # sys.stdout = output_buffer
        # sys.stderr = output_buffer
        thread_local_output = threading.local()
        thread_local_output.buffer = io.StringIO()  # Thread-local buffer
        with stdout_lock:
            with contextlib.redirect_stdout(thread_local_output.buffer):
                cur_env.before_execution()
                program.eval(cur_env)
                cur_env.after_execution()

            expected_res = thread_local_output.buffer.getvalue()
        res = list(filter(None, expected_res.split("\n")))

        if len(res) > 0:
            self.result = res[-1]
        else:
            self.result = "ERROR!"

        # with contextlib.redirect_stdout(output_buffer):
        #    cur_env.before_execution()
        #    program.eval(cur_env)
        #    cur_env.after_execution()
        #    expectedRes = output_buffer.getvalue()
        #    res = list(filter(None, expectedRes.split("\n")))
        #    if len(res) > 0:
        #        self.result = res[-1]
        #    else:
        #        self.result = "ERROR!"

    def get_statements(self, dump_dir="resources/dump_dir", env=None):
        program, cmp_store = Parser.parse(self.code)
        cur_env: Environment = env
        cur_env._exec_mode._dump_dir = dump_dir
        cur_env.before_execution()
        program.eval(cur_env)
        cur_env.after_execution()
