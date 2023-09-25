from protocol.user.era_user import ERAUser
from protocol.user.malicious_user import MaliciousUser
from protocol.user.normal_user import NormalUser
from protocol.user.user_type import UserType


class UserFactory:
    @staticmethod
    def create_user(user_type: UserType, ecs, run_args):
        match user_type:
            case UserType.Normal:
                return NormalUser(ecs, run_args)
            case UserType.Malicious:
                return MaliciousUser(ecs, run_args)
            case UserType.ERA:
                return ERAUser(ecs, run_args)
