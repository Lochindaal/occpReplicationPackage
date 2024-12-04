import jsonlines
import numpy as np
from tqdm import tqdm


class CalculateGasCostsRQ2:
    def __init__(self, input_file: str) -> None:
        self.input_file = input_file  # "./data/results/occp/all_transaction_logs.jsonl"
        # self.approach = approach
        # self.output_file = "./data/results/occp/gas_costs.jsonl"
        self.key_count = {}
        self.add_task_seq = {}
        self.add_traces = {}
        self.get_workload = {}
        self.vote = {}
        self.upload_sequences = {}
        self.upload_conflicts = {}
        self.transaction_costs = {}

    def load_input_data(self):
        data = []
        counter = 0
        with jsonlines.open(self.input_file) as reader:
            for obj in reader:
                data.append(obj)
                counter += 1
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

            if key not in self.key_count:
                self.key_count[key] = {"entries": [], "count": 0}
            else:
                self.key_count[key]["entries"].append(obj["key"])
                self.key_count[key]["count"] = len(set(self.key_count[key]["entries"]))

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

    def format_number(self, num):
        if not np.isnan(num):
            return np.round(num / (10**6), 3)
        else:
            return 0.0

    def compute_average(self):
        averages = []

        for key in tqdm(self.transaction_costs.keys(), desc="Computing averages"):
            try:
                data = {
                    "key": key,
                    "averages": {
                        "total_costs": {
                            "average": np.sum(self.transaction_costs[key])
                            / self.key_count[key]["count"],
                            "average_formatted": self.format_number(
                                np.sum(self.transaction_costs[key])
                                / self.key_count[key]["count"]
                            ),
                            "mean": (
                                np.mean(self.transaction_costs[key])
                                if len(self.transaction_costs[key]) > 0
                                else 0
                            ),
                        },
                        "add_task": {
                            "average": np.sum(self.add_task_seq[key])
                            / self.key_count[key]["count"],
                            "average_formatted": self.format_number(
                                np.sum(self.add_task_seq[key])
                                / self.key_count[key]["count"]
                            ),
                            "mean": (
                                np.mean(self.add_task_seq[key])
                                if len(self.add_task_seq[key]) > 0
                                else 0
                            ),
                        },
                        "add_traces": {
                            "average": np.sum(self.add_traces[key])
                            / self.key_count[key]["count"],
                            "average_formatted": self.format_number(
                                np.sum(self.add_traces[key])
                                / self.key_count[key]["count"]
                            ),
                            "mean": (
                                np.mean(self.add_traces[key])
                                if len(self.add_traces[key]) > 0
                                else 0
                            ),
                        },
                        "vote": {
                            "average": np.sum(self.vote[key])
                            / self.key_count[key]["count"],
                            "average_formatted": self.format_number(
                                np.sum(self.vote[key]) / self.key_count[key]["count"]
                            ),
                            "mean": (
                                np.mean(self.vote[key])
                                if len(self.vote[key]) > 0
                                else 0
                            ),
                        },
                        "get_workload": {
                            "average": np.sum(self.get_workload[key])
                            / self.key_count[key]["count"],
                            "average_formatted": self.format_number(
                                np.sum(self.get_workload[key])
                                / self.key_count[key]["count"]
                            ),
                            "mean": (
                                np.mean(self.get_workload[key])
                                if len(self.get_workload[key]) > 0
                                else 0
                            ),
                        },
                        "upload_sequence": {
                            "average": np.sum(self.upload_sequences[key])
                            / self.key_count[key]["count"],
                            "average_formatted": self.format_number(
                                np.sum(self.upload_sequences[key])
                                / self.key_count[key]["count"]
                            ),
                            "mean": (
                                np.mean(self.upload_sequences[key])
                                if len(self.upload_sequences[key]) > 0
                                else 0
                            ),
                        },
                        "upload_conflicts": {
                            "average": np.sum(self.upload_conflicts[key])
                            / self.key_count[key]["count"],
                            "average_formatted": self.format_number(
                                np.sum(self.upload_conflicts[key])
                                / self.key_count[key]["count"]
                            ),
                            "mean": (
                                np.mean(self.upload_conflicts[key])
                                if len(self.upload_conflicts[key]) > 0
                                else 0
                            ),
                        },
                    },
                }
                averages.append(data)
            except Exception as e:
                print(e)
        return averages

    def persist(self, path, data):
        with jsonlines.open(path, mode="w") as writer:
            writer.write_all(data)

    def run(self):
        self.compute_sum()
        averages = self.compute_average()
        return averages
        # self.persist(self.output_file, averages)
