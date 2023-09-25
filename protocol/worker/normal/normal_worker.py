import hashlib
import os
import pickle
import time
from abc import ABC
from threading import Thread

from protocol.tasks.task_runner import TaskRunner
from protocol.worker.base_worker import BaseWorker

DEBUG = False


class NormalWorker(BaseWorker, ABC):

    def __init__(self, worker_id, ecs, kill_all, run_args):
        super().__init__(worker_id, ecs, kill_all, run_args, 1)

    def work(self):
        start_time = time.time()
        workload = self.get_workload()
        self.data_writer.write_data(self.worker_id, 1, (time.time() - start_time), self.client_type.name)
        if workload is None:
            return
        task_id = workload["taskId"]
        trace_id = workload["traceId"]
        self.logger.info(
            f"Certifier {self.worker_id} working on trace {trace_id} from task {task_id}"
        )
        runner = TaskRunner(workload)
        error = False
        try:
            # re-execute partial trace
            start_time = time.time()
            self.replay_task(
                Thread(target=runner.run, args=[self.work_dir]),
                task_id,
                trace_id,
                self.logger,
            )
            self.data_writer.write_data(self.worker_id, 3, (time.time() - start_time), self.client_type.name)
            # if DEBUG:
            self.logger.debug(
                f"--- {(time.time() - start_time)} seconds to replay snapshot"
                f" [TaskId: {task_id} TraceId: {trace_id}]---"
            )

            generated_env = self.load_output(runner.startEnv._exec_mode._snap_id)
            # ToDo: Write required stmts in a separate file for easier inspection
            executed_stmts = generated_env._exec_mode.run_stmts
            self.logger.info(
                f"Replay of Task {task_id} Trace {trace_id} required {executed_stmts} stmts"
            )

            # stmts_path = os.path.join(self.config["DATA"]["OccpResultDir"], "stmts.json")
            self.data_writer.write_data(self.worker_id, 4, executed_stmts, self.client_type.name)
            # write_thread_safe({f"{self.worker_id}_{task_id}_{trace_id}": executed_stmts}, stmts_path)
            result_dict = generated_env.__dict__
            del result_dict["_exec_mode"]
        except Exception as e:
            self.logger.error(e)
            error = True
        if error:
            target_hash = hashlib.sha256("ERROR".encode()).digest()
            self.logger.error(
                f"Error while replaying Trace {trace_id} of Task {task_id}"
            )
        else:
            target_hash = hashlib.sha256(pickle.dumps(result_dict)).digest()

        self.send_result(task_id, trace_id, target_hash)

        return task_id, trace_id

    def load_output(self, trace_id):
        file_path = os.path.join(self.work_dir, f"{trace_id}_out_snap.pickle")
        with open(file_path, "rb") as handler:
            env = pickle.load(handler)
        return env

    @staticmethod
    def replay_task(thread, task_id, trace_id, logger):
        start_time = time.time()
        thread.start()
        thread.join()
        logger.info(
            f"--- {(time.time() - start_time)} seconds to replay snapshot [TaskId: {task_id} TraceId: {trace_id}]---"
        )

# # ToDo: stop job certifiers if there are no openTasks anymore
# # ToDo: check removeTask function in solidiy contract (0 remains for some reason)
