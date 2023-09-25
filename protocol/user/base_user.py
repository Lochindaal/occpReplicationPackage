import hashlib
import os
import pickle
import random
import uuid

from eth_abi.packed import encode_packed
from mona.interpreter.environment.environment import Environment, ExecModeRecord
from mona.interpreter.parsing.parser import Parser

from protocol.storage.data_storage import DataStorage
from protocol.storage.file_system_storage import FileSystemStorage
from protocol.tasks.task_creator import TaskCreator
from protocol.utils.config_utils import load_config
from utils.trace_utils import compute_trace_hash


class BaseUser:
    def __init__(self, ecs, run_args):
        self.ecs = ecs
        self.storage_fs = FileSystemStorage()
        self.config = load_config()
        self.storage_s3 = DataStorage(self.config["STORAGE"]["BucketName"])
        self.run_args = run_args

    def load_traces(self):
        program_dir = (
            f"{self.run_args['key']}_{self.run_args['steps']}"
            if self.run_args["steps"] > 0
            else self.run_args["key"]
        )
        trace_path = os.path.join(load_config()["EXPERIMENT"]["DumpDir"], program_dir)
        return self.storage_fs.load_all_traces(trace_path)

    def load_task_data(self):
        source_code = self.storage_fs.load_source_code(self.run_args["key"])
        traces = self.load_traces()
        return source_code, traces

    def store_task_data(self, task_data):
        source_code, traces = task_data
        task_uuid = uuid.uuid1()
        trace_location = self.storage_s3.store_trace_list(task_uuid, traces)
        src_location = f"{task_uuid}_code"
        self.storage_s3.save(pickle.dumps(source_code), src_location)
        return task_uuid, src_location, trace_location

    def run(self):
        # load traces and store them on S3
        task_data = self.load_task_data()
        task_uuid, src_location, trace_location = self.store_task_data(task_data)
        # prepare sequence hash H and shuffle the traces without the target trace
        shuffled_traces, sequence_hash, all_hashes = self.prepare_traces(trace_location)

        # upload a certification task to occp
        task_id = self.upload_task(shuffled_traces, sequence_hash, src_location)

        return {
            "TaskId": task_id,
            "TaskUUID": task_uuid,
            "payload": {
                "source_loc": src_location,
                "sequenceH": sequence_hash,
                "traces": trace_location,
                "shuffled": shuffled_traces,
                "input_hash": all_hashes[0],
                "target_hash": all_hashes[len(all_hashes) - 1],
            },
        }

    @staticmethod
    def eval_program(program, env):
        env.before_execution()
        program.eval(env)
        env.after_execution()

    @staticmethod
    def load_program(path):
        with open(path, "r") as df:
            src = df.read()
        return Parser.parse(src)

    def execute_local_run(self):
        # ToDo: add as option to run the trace recording directly from the user
        # ToDo: Make sure to remove existing data in the directory!
        key = self.run_args["key"]
        steps = self.run_args["steps"]
        path = os.path.join(self.config["EXPERIMENT"]["ProgramBaseDir"], f"{key}.mona")
        # dump_dir = os.path.join(self.config["EXPERIMENT"]["DumpDir"], key)
        program_dir = (
            f"{self.run_args['key']}_{self.run_args['steps']}"
            if self.run_args["steps"] > 0
            else self.run_args["key"]
        )
        trace_path = os.path.join(load_config()["EXPERIMENT"]["DumpDir"], program_dir)
        program, _ = self.load_program(path)
        exec_mode = ExecModeRecord(dump_dir=trace_path, steps=steps)
        env = Environment(exec_mode=exec_mode)
        env.before_execution()
        program.eval(env)
        env.after_execution()

    def create_sequence_hash(self, sequence_list):
        sequence_hashes = []
        for i in range(len(sequence_list)):
            sequence_hashes.append(compute_trace_hash(sequence_list[i]["trace"]))
        sequence_hash = hashlib.sha256(
            encode_packed(["bytes32[]"], [sequence_hashes])
        ).digest()
        return sequence_hash, sequence_hashes

    def prepare_traces(self, traces):
        sequence_hash, all_hashes = self.create_sequence_hash(traces)
        # result_trace = traces[len(traces) - 1]
        del traces[len(traces) - 1]

        upl_traces = []
        for key, trace in traces.items():
            upl_traces.append(
                {
                    "traceId": key + 1,  # ToDo make traceId random but unique and within range of max snapshots!
                    "traceLocation": str(trace["location"]),
                    "startTraceHash": hashlib.sha256(
                        pickle.dumps(trace["trace"].__dict__)
                    ).digest(),
                }
            )
        shuffled_traces = self.shuffle_traces(upl_traces)
        return shuffled_traces, sequence_hash, all_hashes

    @staticmethod
    def shuffle_traces(trace_list):
        # trace_locations = [x['location'] for x in trace_list.values()]
        random.shuffle(trace_list)
        return trace_list

    def upload_task(self, trace_list, sequence_hash, src_location):
        return TaskCreator(self.ecs).add_task(trace_list, sequence_hash, src_location)
