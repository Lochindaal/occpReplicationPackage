import hashlib
import logging
import os
import time

from eth_abi.packed import encode_packed

from protocol.utils.config_utils import load_config
from protocol.worker.ecs import prepare_traces


def load_source_code(program_name):
    with open(os.path.join("./data/programs", f"{program_name}.mona")) as handler:
        src = handler.read()
    return src


class TaskCreator:
    def __init__(self, ecs_client):
        self.client = ecs_client
        self.config = load_config()
        self.logger = logging.getLogger(self.config["LOGGING"]["LogName"])

    def add_new_task(self, task_data):
        _, snapshots, trace_storage_location, _, src = task_data
        self.logger.info("--- Adding tasks")
        traces, sequence_hashes = prepare_traces(
            snapshots, trace_storage_location, self.config["MALICIOUS"]["User"]
        )

        target_sequence = hashlib.sha256(
            encode_packed(["bytes32[]"], [sequence_hashes])
        ).digest()
        cert_hash = hashlib.sha256("myCertificate".encode()).digest()
        if len(traces) > 20:
            start_time = time.time()
            task_id = self.client.add_task_seq([src, [], target_sequence, cert_hash, []])

            self.logger.info(f"--- {(time.time() - start_time)} seconds to upload task")
            start_time2 = time.time()
            n = 20
            trace_split = [traces[i: i + n] for i in range(0, len(traces), n)]
            start = 0
            for traceList in trace_split:
                self.client.add_traces(task_id, traceList)
                start += len(traceList)
            self.logger.info(
                f"--- {(time.time() - start_time2)} seconds to upload {len(traces)} traces"
            )
        else:
            start_time = time.time()
            task_id = self.client.add_task_seq(
                [
                    src,
                    traces,
                    target_sequence,
                    cert_hash,
                    list(range(1, len(traces) + 1)),
                ]
            )

        self.logger.info(
            f"--- {(time.time() - start_time)} seconds to upload Task with {len(traces)} traces"
        )

        return task_id, traces, target_sequence, sequence_hashes

    def add_task(self, trace_list, sequence_hash, src_location):
        cert_hash = hashlib.sha256("myCertificate".encode()).digest()
        if len(trace_list) > 20:
            start_time = time.time()
            task_id = self.client.add_task_seq(
                [src_location, [], sequence_hash, cert_hash, []]
            )

            self.logger.info(f"--- {(time.time() - start_time)} seconds to upload task")
            start_time2 = time.time()
            n = 20
            trace_split = [trace_list[i: i + n] for i in range(0, len(trace_list), n)]
            start = 0
            for traceList in trace_split:
                self.client.add_traces(task_id, traceList)
                start += len(traceList)
            self.logger.info(
                f"--- {(time.time() - start_time2)} seconds to upload {len(trace_list)} traces"
            )
        else:
            start_time = time.time()
            task_id = self.client.add_task_seq(
                [
                    src_location,
                    trace_list,
                    sequence_hash,
                    cert_hash,
                    list(range(1, len(trace_list) + 1)),
                ]
            )

        self.logger.info(
            f"--- {(time.time() - start_time)} seconds to upload Task with {len(trace_list)} traces"
        )
        return task_id
