from protocol.user.base_user import BaseUser


class NormalUser(BaseUser):
    def __init__(self, ecs, run_args):
        super().__init__(ecs, run_args)
