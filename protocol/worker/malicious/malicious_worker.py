import random

from protocol.worker.base_worker import BaseWorker


class MaliciousWorker(BaseWorker):
    def __init__(self, worker_id, ecs, kill_all, run_args):
        self.lazy_count = 0
        super().__init__(worker_id, ecs, kill_all, run_args, 2)

    def work(self):
        workload = self.get_workload()
        if workload is None:
            return

        task_id = workload["taskId"]
        trace_id = workload["traceId"]
        self.logger.info(f"Lazy worker working on Task{task_id}/Trace{trace_id}")
        target_hash, target_trace_id = self.get_random_hash(task_id, trace_id)
        if target_hash is None:
            return

        self.send_result(task_id, trace_id, target_hash)
        self.lazy_count += 1
        self.logger.info(
            f"Lazy worker sent {target_trace_id} for Trace {trace_id} of Task {task_id}"
        )
        if self.lazy_count >= self.config.getint("NODES", "LazyWork"):
            self.loop_break = True

    def get_random_hash(self, task_id, trace_id):
        tasks = self.ecs.get_tasks()
        for task in tasks:
            if task[0] == task_id:
                my_task = task
                break
        if len(my_task) > 1:
            filtered_traces = [x for x in my_task[2] if x[0] != trace_id and x[0] > 1]
            random_result_trace = random.choice(filtered_traces)
            return random_result_trace[2], random_result_trace[0]
        else:
            return None
