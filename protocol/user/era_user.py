from protocol.user.base_user import BaseUser


class ERAUser(BaseUser):
    def __init__(self, ecs, run_args):
        self.alternative_code = run_args["alt_code"]
        super().__init__(ecs, run_args)

    def load_task_data(self):
        source_code = self.storage_fs.load_source_code(self.alternative_code)
        traces = self.load_traces()
        return source_code, traces
