from naive.ecs import ExecutionCertificationSystemNaive
from protocol.utils.config_utils import load_config
from protocol.worker.ecs import ExecutionCertificationSystem


def init_ecs(addy="http://127.0.0.1:10002", contract="", run_args=None, is_naive=False):
    # Blockchain network
    chain_address = addy
    account = "0x9308aB927A9ce7E23CC6de5F2c7500b25185defF"

    if is_naive:
        config = load_config("occp_naive.ini")
        ecs_contract = (
            contract if contract != "" else config["NETWORK"]["ContractAddress"]
        )
        return ExecutionCertificationSystemNaive(
            ecs_contract,
            config["NETWORK"]["AbiLocation"],
            chain_address,
            account,
            run_args,
        )
    else:
        config = load_config()
        ecs_contract = (
            contract if contract != "" else config["NETWORK"]["ContractAddress"]
        )
        return ExecutionCertificationSystem(
            ecs_contract,
            config["NETWORK"]["AbiLocation"],
            chain_address,
            account,
            run_args,
        )
