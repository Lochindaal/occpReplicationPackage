import numpy as np
import json
from tqdm import tqdm
import jsonlines


class CalculateWorkerStatsRQ2:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.key_count = {}
        self.stmts_val = {}
        self.statement_sum = {}
        self.statement_count = {}
        self.workload_sum = {}
        self.workload_count = {}
        self.replay_sum = {}
        self.replay_count = {}
        self.vote_sum = {}
        self.vote_count = {}

    def compute_sum_count(self):
        # Read the JSON lines file
        counter = 0
        with open(self.input_file, "r") as file:
            for line in tqdm(file, desc="Computing sum and count"):
                counter += 1
                try:
                    data = json.loads(line)
                except Exception as e:
                    print(line)
                    raise e

                parts = data["key"].split("_")
                key = "_".join(parts[:-1])
                if key not in self.key_count:
                    self.key_count[key] = {"entries": [], "count": 0}
                else:
                    self.key_count[key]["entries"].append(data["key"])
                    self.key_count[key]["count"] = len(
                        set(self.key_count[key]["entries"])
                    )
                entry_type = data["Type"]
                if entry_type == "STMTS":
                    values = data["Statements"]
                else:
                    values = data["Time"]
                if key not in self.statement_sum:
                    self.stmts_val[key] = []
                    self.statement_sum[key] = 0
                    self.statement_count[key] = 0
                    self.workload_sum[key] = 0
                    self.workload_count[key] = 0
                    self.vote_sum[key] = 0
                    self.vote_count[key] = 0
                    self.replay_sum[key] = 0
                    self.replay_count[key] = 0

                # Calculate and update the sum and count for each type
                if entry_type == "STMTS":
                    self.stmts_val[key].append(values)
                    self.statement_sum[key] += values
                    self.statement_count[key] += 1
                if entry_type == "VOTE":
                    self.vote_sum[key] += values
                    self.vote_count[key] += 1
                if entry_type == "REPLAY":
                    self.replay_sum[key] += values
                    self.replay_count[key] += 1
                if entry_type == "WORKLOAD":
                    self.workload_sum[key] += values
                    self.workload_count[key] += 1

    def compute_average(self):
        averages = []
        for key in tqdm(self.statement_sum.keys(), desc="Computing average"):
            data = {
                "key": key,
                "avg_stmts": self.statement_sum[key] / self.key_count[key]["count"],
                "avg_stmts_count": self.statement_count[key]
                / self.key_count[key]["count"],
                "mean_stmts": np.mean(self.stmts_val[key]),
                "median_stmts": np.median(self.stmts_val[key]),
                "var_stmts": np.var(self.stmts_val[key]),
                "std_stmts": np.std(self.stmts_val[key]),
                "avg_workload": self.workload_sum[key] / self.key_count[key]["count"],
                "avg_workload_count": self.workload_count[key]
                / self.key_count[key]["count"],
                "avg_replay": self.replay_sum[key] / self.key_count[key]["count"],
                "avg_replay_count": self.replay_count[key]
                / self.key_count[key]["count"],
                "avg_vote": self.vote_sum[key] / self.key_count[key]["count"],
                "avg_vote_count": self.vote_count[key] / self.key_count[key]["count"],
            }
            averages.append(data)

        return averages

    # def persist(self, averages):
    #    with jsonlines.open(self.target_file, mode="w") as writer:
    #        writer.write_all(averages)

    def run(self):
        self.compute_sum_count()
        averages = self.compute_average()
        return averages
        # self.persist(averages)


# def main():
#    calc = CalculateWorkerStatsRQ2()
#    calc.run()

#
# if __name__ == "__main__":
#    main()
