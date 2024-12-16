import os
import pickle
import time
import random
from abc import ABC
from threading import Thread

from naive.taks_runner_naive import TaskRunnerNaive
from naive.base_worker_naive import BaseWorkerNaive

DEBUG = False


class NaiveNormalWorker(BaseWorkerNaive, ABC):

    def __init__(self, worker_id, ecs, kill_all, run_args):
        super().__init__(worker_id, ecs, kill_all, run_args, 1)

    def work(self):
        start_time = time.time()
        workload = self.get_workload()
        self.data_writer.write_data(
            self.worker_id, 1, (time.time() - start_time), self.client_type.name
        )
        if workload is None:
            if self.sleep_time < 10:
                self.sleep_time += 1
            return

        if self.killAll.isSet():
            return
        task_id = workload["taskId"]
        expectedResult = workload["expectedResult"]
        computed_result = "FAIL"
        self.logger.info(f"Naive Certifier {self.worker_id} working on task {task_id}")
        runner = TaskRunnerNaive(workload)
        error = False
        try:
            start_time = time.time()
            self.replay_task(
                Thread(target=runner.run, args=[self.work_dir]),
                task_id,
                self.logger,
            )
            computed_result = runner.result
            if computed_result is None or computed_result == "ERROR!":
                print(computed_result)
            self.data_writer.write_data(
                self.worker_id, 3, (time.time() - start_time), self.client_type.name
            )
            # if DEBUG:
            self.logger.debug(
                f"--- {(time.time() - start_time)} seconds to replay snapshot"
                f" [TaskId: {task_id}]---"
            )

            start_env = self.load_output(0, False)
            self.replay_task(
                Thread(target=runner.get_statements, args=[self.work_dir, start_env]),
                task_id,
                self.logger,
            )
            generated_env = self.load_output(0)

            # ToDo: Write required stmts in a separate file for easier inspection
            #executed_stmts = generated_env._exec_mode.stmts_run
            executed_stmts = generated_env._exec_mode.run_stmts
            #executed_stmts = generated_env._exec_mode.run_stmts
            #executed_stmts = generated_env.__dict__["_exec_mode"].run_stmts
            self.logger.info(
                f"Replay of Task {task_id} required {executed_stmts} stmts"
            )

            # stmts_path = os.path.join(self.config["DATA"]["OccpResultDir"], "stmts.json")
            self.data_writer.write_data(
                self.worker_id, 4, executed_stmts, self.client_type.name
            )
            # write_thread_safe({f"{self.worker_id}_{task_id}_{trace_id}": executed_stmts}, stmts_path)
            result_dict = generated_env.__dict__
            del result_dict["_exec_mode"]
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"Error while replaying Task {task_id}")
            error = True

        if not error and computed_result == expectedResult:
            self.send_result(task_id, True)
        else:
            self.send_result(task_id, False)

        return task_id

    def load_output(self, trace_id, is_out=True):
        if is_out:
            file_path = os.path.join(self.work_dir, f"{trace_id}_out_snap.pickle")
        else:
            file_path = os.path.join(self.work_dir, f"{trace_id}_snap.pickle")
        with open(file_path, "rb") as handler:
            env = pickle.load(handler)
        return env

    @staticmethod
    def replay_task(thread, task_id, logger):
        start_time = time.time()
        thread.start()
        thread.join()
        logger.info(
            f"--- {(time.time() - start_time)} seconds to replay snapshot [TaskId: {task_id}]---"
        )
