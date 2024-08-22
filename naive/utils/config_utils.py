import configparser
from functools import lru_cache


@lru_cache(maxsize=None)
def load_config(config_file="occp_naive.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config
