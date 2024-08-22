from protocol.worker.naive.base_worker_naive import BaseWorkerNaive


class NaiveMaliciousWorker(BaseWorkerNaive):
    def __init__(self, worker_id, ecs, kill_all, run_args):
        super().__init__(worker_id, ecs, kill_all, run_args, 2)

    def work(self):
        workload = self.get_workload()
        if workload is None:
            if self.sleep_time < 20:
                self.sleep_time += 1
            return

        task_id = workload["taskId"]
        self.logger.info(
            f"Naive Lazy worker ({self.worker_id}) working on Task{task_id}"
        )
        self.send_result(task_id, False)
        self.logger.info(
            f"Lazy worker ({self.worker_id}) sent {False} for Task {task_id}"
        )
