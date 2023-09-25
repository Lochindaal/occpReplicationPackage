from protocol.utils.config_utils import load_config
from protocol.worker.ecs import ExecutionCertificationSystem


def init_ecs(addy="http://127.0.0.1:10002", contract=""):
    # Blockchain network
    chain_address = addy
    account = "0x9308aB927A9ce7E23CC6de5F2c7500b25185defF"
    ecs_contract = (
        contract if contract != "" else load_config()["NETWORK"]["ContractAddress"]
    )
    return ExecutionCertificationSystem(
        ecs_contract, load_config()["NETWORK"]["AbiLocation"], chain_address, account
    )
