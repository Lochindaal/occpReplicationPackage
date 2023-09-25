from enum import Enum

from runner.local_runner import LocalRunner
from runner.occp_runner import OCCPRunner


class RunnerType(Enum):
    LOCAL = 1
    OCCP = 2


class RunnerFactory:
    @staticmethod
    def get_runner(runner_type: RunnerType, address_list):
        match runner_type:
            case RunnerType.LOCAL:
                return LocalRunner()
            case RunnerType.OCCP:
                return OCCPRunner(address_list)
