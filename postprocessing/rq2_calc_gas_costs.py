import jsonlines
import numpy as np
import json
from tqdm import tqdm


class CalculateGasCostsRQ2:
    def __init__(self) -> None:
        self.input_file = "./data/results/occp/all_transactions.jsonl"
        self.output_file = "./data/results/occp/gas_costs.jsonl"
        self.add_task_seq = {}
        self.add_traces = {}
        self.get_workload = {}
        self.vote = {}
        self.upload_sequences = {}
        self.upload_conflicts = {}
        self.transaction_costs = {}

    def load_input_data(self):
        data = []
        with jsonlines.open(self.input_file) as reader:
            for obj in reader:
                data.append(obj)
        return data

    def compute_sum(self):
        try:
            data = self.load_input_data()
        except Exception as e:
            print(e)
            raise e

        for obj in tqdm(data, desc="Computing sum"):
            parts = obj["key"].split("_")
            key = "_".join(parts[:-1])
            entry_type = obj["function"]
            value = obj["gasUsed"]

            if key not in self.transaction_costs:
                self.add_task_seq[key] = []
                self.add_traces[key] = []
                self.get_workload[key] = []
                self.vote[key] = []
                self.upload_sequences[key] = []
                self.upload_conflicts[key] = []
                self.transaction_costs[key] = []

            match entry_type:
                case "add_task_seq":
                    self.add_task_seq[key].append(value)
                    self.transaction_costs[key].append(value)
                case "add_traces":
                    self.add_traces[key].append(value)
                    self.transaction_costs[key].append(value)
                case "get_workload_seq":
                    self.get_workload[key].append(value)
                    self.transaction_costs[key].append(value)
                case "vote":
                    self.vote[key].append(value)
                    self.transaction_costs[key].append(value)
                case "upload_sequence":
                    self.upload_sequences[key].append(value)
                    self.transaction_costs[key].append(value)
                case "upload_conflicts":
                    self.upload_conflicts[key].append(value)
                    self.transaction_costs[key].append(value)

    def compute_average(self):
        averages = []

        for key in tqdm(self.transaction_costs.keys(), desc="Computing averages"):
            data = {
                "key": key,
                "averages": {
                    "total_costs": {
                        "average": np.sum(self.transaction_costs[key]) / 30,
                        "mean": np.mean(self.transaction_costs[key]),
                    },
                    "add_task": {
                        "average": np.sum(self.add_task_seq[key]) / 30,
                        "mean": np.mean(self.add_task_seq[key]),
                    },
                    "add_traces": {
                        "average": np.sum(self.add_traces[key]) / 30,
                        "mean": np.mean(self.add_traces[key]),
                    },
                    "vote": {
                        "average": np.sum(self.vote[key]) / 30,
                        "mean": np.mean(self.vote[key]),
                    },
                    "get_workload": {
                        "average": np.sum(self.get_workload[key]) / 30,
                        "mean": np.mean(self.get_workload[key]),
                    },
                    "upload_sequence": {
                        "average": np.sum(self.upload_sequences[key]) / 30,
                        "mean": np.mean(self.upload_sequences[key]),
                    },
                    "upload_conflicts": {
                        "average": np.sum(self.upload_conflicts[key]) / 30,
                        "mean": np.mean(self.upload_conflicts[key]),
                    },
                },
            }
            averages.append(data)
        return averages

    def persist(self, path, data):
        with jsonlines.open(path, mode="w") as writer:
            writer.write_all(data)
        # with open(path, "w") as f:
        #    for obj in data:
        #        json.dump(obj, f, indent=3)
        #        f.write("\n")

    def run(self):
        self.compute_sum()
        averages = self.compute_average()
        self.persist(self.output_file, averages)
