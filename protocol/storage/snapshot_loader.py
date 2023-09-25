import os
import pickle

from mona.interpreter.environment.environment import Environment

# ToDo: delete this class!

class SnapshotLoader:
    def __init__(self, snapshot_path):
        self.base_path = snapshot_path

    def load_snapshots(self):
        snapshots = []
        for filename in os.listdir(self.base_path):
            if "out" not in filename:
                with open(
                        os.path.join(self.base_path, filename), "rb"
                ) as f:  # open in readonly mode
                    env: Environment = pickle.load(f)
                    snapshots.append(env)

        return sorted(snapshots, key=lambda x: x._exec_mode._snap_id, reverse=False)
