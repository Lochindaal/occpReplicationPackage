import logging
import os
import random
import time
from abc import abstractmethod
from enum import Enum

from protocol.utils.config_utils import load_config
from protocol.utils.data_writer_utils import DataWriterHelper
from protocol.utils.fs_utils import create_directory


# class syntax
class ClientType(Enum):
    NORMAL = 1
    MALICIOUS = 2


class BaseWorker:
    def __init__(self, worker_id, ecs, kill_all, run_args, client_type):
        self.ecs = ecs
        self.worker_id = worker_id
        self.killAll = kill_all
        self.config = load_config()
        self.logger = logging.getLogger(self.config["LOGGING"]["LogName"])
        self.loop_break = False
        self.work_dir = os.path.join(
            self.config["EXPERIMENT"]["DumpDir"], "occp", f"node{self.worker_id}"
        )
        self.data_writer = DataWriterHelper(run_args)
        self.client_type = ClientType(client_type)
        self.run_args = run_args

    def run(self):
        print(f"Certifier/Worker {self.worker_id} started...")
        # self.create_dump_dir()
        create_directory(self.work_dir)
        while not self.killAll.isSet():
            self.work()
            time.sleep(self.config.getint("NODES", "PollInterval"))
            if self.loop_break:
                break
        print(f"Worker {self.worker_id} ended...")

    @abstractmethod
    def work(self):
        pass

    def get_workload(self):
        try:
            return self.ecs.get_workload_seq(self.worker_id)
        except Exception as e:
            self.logger.error(e)
            return None

    def send_result(self, task_id, trace_id, target_hash):
        try:
            # vote accordingly
            start_time = time.time()
            receipt, _ = self.ecs.vote(task_id, trace_id, target_hash, self.worker_id)
            self.logger.info(f"--- {(time.time() - start_time)} seconds to send vote")
            retry_counter = 1
            while receipt.status != 1 and retry_counter < 5:
                retry_counter += 1
                n = random.randint(0, retry_counter)
                time.sleep(n)
                receipt, _ = self.ecs.vote(
                    task_id, trace_id, target_hash, self.worker_id
                )
            self.logger.info(
                f"--- {time.time() - start_time} seconds to vote "
                f"(with {retry_counter - 1} retries) [Task|Trace: {task_id}|{trace_id}] - Target: {target_hash}"
            )
            self.data_writer.write_data(self.worker_id, 2, (time.time()-start_time), self.client_type.name)
        except Exception as e:
            self.logger.error(e)
        return task_id, trace_id

    def create_dump_dir(self):
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
