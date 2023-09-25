from enum import Enum

from web3 import Web3


class Web3ProviderType(Enum):
    HTTP = 1
    Socket = 2


def init_web3_connection(con_type: Web3ProviderType, connection_string):
    if con_type == Web3ProviderType.HTTP:
        provider = Web3.HTTPProvider(connection_string)
    else:
        provider = Web3.WebsocketProvider(connection_string)
    return Web3(provider)
