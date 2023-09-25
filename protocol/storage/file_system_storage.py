import os
import pickle

from mona.interpreter.environment.environment import Environment

from protocol.utils.config_utils import load_config


class FileSystemStorage:
    def __init__(self):
        self.config = load_config()
        self.base_path = self.config["EXPERIMENT"]["DumpDir"]

    def save(self, obj, object_name):
        save_path = os.path.join(self.base_path, object_name)
        with open(save_path, "wb") as handler:
            pickle.dump(obj, handler)
        return True

    @staticmethod
    def load(storage_key):
        with open(storage_key, "rb") as f:
            env: Environment = pickle.load(f)
        return env

    def load_source_code(self, program_name):
        path = os.path.join(
            self.config["EXPERIMENT"]["ProgramBaseDir"], f"{program_name}.mona"
        )
        with open(path) as handler:
            src = handler.read()
        return src

    @staticmethod
    def load_all_traces(storage_location):
        load_list = []
        for filename in os.listdir(storage_location):
            if "out" not in filename:
                with open(
                        os.path.join(storage_location, filename), "rb"
                ) as f:  # open in readonly mode
                    env: Environment = pickle.load(f)
                    load_list.append(env)

        return sorted(load_list, key=lambda x: x._exec_mode._snap_id, reverse=False)
