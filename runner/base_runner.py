import logging
import time
from abc import abstractmethod
from enum import Enum
from threading import Thread

from mona.interpreter.environment.environment import (
    Environment,
    ExecModeRun,
    ExecModeRecord,
)
from mona.interpreter.parsing.parser import Parser

from protocol.storage.storage_factory import StorageFactory
from protocol.utils.config_utils import load_config
from utils.log_utils import init_logger
from utils.trace_utils import compare_traces_for_index


class RunType(Enum):
    RUN = 1
    RUN_RECORD = 2
    RUN_REPLAY = 3


class BaseRunner:
    def __init__(self, runner_type: int):
        self.config = load_config()
        self.base_path = self.config["DATA"]["ResultBaseDir"]
        self.storage = StorageFactory.get_storage(runner_type)
        self.logger = init_logger()
        # self.logger = logging.Logger(self.config["LOGGING"]["LogName"])

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def get_exec_mode(exec_type: RunType, mode_args):
        match exec_type:
            case RunType.RUN:
                return ExecModeRun(dump_dir=mode_args["dump_dir"])
            case RunType.RUN_RECORD:
                return ExecModeRecord(
                    dump_dir=mode_args["dump_dir"], steps=mode_args["steps"]
                )
        return None

    @staticmethod
    def load_program(path):
        with open(path, "r") as df:
            src = df.read()
        return Parser.parse(src)

    def execute_program(self, path, run_type, dump_dir, steps):
        program, _ = self.load_program(path)
        mode_args = {"dump_dir": dump_dir, "steps": steps}
        if run_type == RunType.RUN_REPLAY:
            self.replay_program(dump_dir, program, mode_args)
        else:
            self.run_program(program, run_type, mode_args, env=None)

    def replay_program(self, dump_dir, program, mode_args):
        env_list = self.storage.load_all_traces(
            dump_dir
        )
        replay_time = []
        for idx, env in enumerate(env_list):
            if idx >= (len(env_list) - 1):
                break
            trace_replay_time = time.time()
            t = Thread(
                target=self.run_program,
                args=(program, RunType.RUN_REPLAY, mode_args, env),
            )
            t.start()
            t.join()
            replay_time.append(time.time() - trace_replay_time)
            compare_traces_for_index(idx, dump_dir, self.storage, self.logger)
        return replay_time

    def run_program(self, program, run_type: RunType, mode_args, env=None):
        if env is not None:
            env._exec_mode._dump_dir = mode_args["dump_dir"]
        else:
            exec_mode = self.get_exec_mode(run_type, mode_args)
            env = Environment(exec_mode=exec_mode)
        env.before_execution()
        program.eval(env)
        env.after_execution()
