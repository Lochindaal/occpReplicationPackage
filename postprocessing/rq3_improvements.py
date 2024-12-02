import numpy as np
import pandas as pd

from postprocessing.commons import get_key_parts


class Rq3Improvements:

    def __init__(self) -> None:
        self.step_size_naive = "100000000000"
        pass

    def get_entry(self, key, data):
        for entry in data:
            if entry["key"] == key:
                return entry
        return None

    def create_scenario_lists(self, data_naive, data_occp, key):
        scenario_lists = {
            "All": {"all": [], "1": [], "10": [], "100": [], "1000": []},
            "HappyCase": {"all": [], "1": [], "10": [], "100": [], "1000": []},
            "MaliciousUser": {"all": [], "1": [], "10": [], "100": [], "1000": []},
            "LazyWorker_10": {"all": [], "1": [], "10": [], "100": [], "1000": []},
            "LazyWorker_20": {"all": [], "1": [], "10": [], "100": [], "1000": []},
            "LazyWorker_30": {"all": [], "1": [], "10": [], "100": [], "1000": []},
            "LazyWorker_40": {"all": [], "1": [], "10": [], "100": [], "1000": []},
        }
        for entry in data_occp:
            key_parts = entry["key"].split("_")
            _, scenario, multiplier, _ = get_key_parts(entry["key"])
            naive_key = "_".join(key_parts[:-1]) + f"_{self.step_size_naive}"
            naive_entry = self.get_entry(naive_key, data_naive)
            if naive_entry is None:
                continue

            if "LazyWorkerPercentage" in scenario:
                scenario = scenario.replace("Percentage", "")

            scenario_lists[scenario]["all"].append((naive_entry[key], entry[key]))
            scenario_lists[scenario][multiplier].append((naive_entry[key], entry[key]))

            scenario_lists["All"]["all"].append((naive_entry[key], entry[key]))
            scenario_lists["All"][multiplier].append((naive_entry[key], entry[key]))
        return scenario_lists

    def calculate_stats(self, name, data: list[tuple[float, float]]):
        # Relative increase/decrease in percentage
        naive = np.array([x[0] for x in data])
        ours = np.array([x[1] for x in data])
        relative_change = (ours - naive) / naive * 100  # In percentage
        relative_change[naive == 0] = np.nan  # Handle division by zero cases

        if len(relative_change) == 0:
            return {}, []
        # Magnitude increase/decrease
        magnitude_change = np.abs(ours - naive)

        # Fold increase/decrease
        # fold_change = ours / naive
        fold_change = naive / ours
        fold_change[naive == 0] = (
            np.inf
        )  # Handle division by zero cases (infinite fold change)

        # Summary statistics for analysis
        stats = {
            "Mean Relative Change (%)": np.nanmean(relative_change).tolist(),
            "Median Relative Change (%)": np.nanmedian(relative_change).tolist(),
            "Min Relative Change (%)": np.nanmin(relative_change).tolist(),
            "Max Relative Change (%)": np.nanmax(relative_change).tolist(),
            "Mean Magnitude Change": np.nanmean(magnitude_change).tolist(),
            "Median Magnitude Change": np.nanmedian(magnitude_change).tolist(),
            "Min Magnitude Change": np.nanmin(magnitude_change).tolist(),
            "Max Magnitude Change": np.nanmax(magnitude_change).tolist(),
            "Mean Fold Change": np.nanmean(fold_change).tolist(),
            "Median Fold Change": np.nanmedian(fold_change).tolist(),
            "Min Fold Change": np.nanmin(fold_change).tolist(),
            "Max Fold Change": np.nanmax(fold_change).tolist(),
        }

        # Convert to DataFrame for better representation
        summary_df = pd.DataFrame([stats])

        # Print results
        # print(f"Summary Statistics for {name}:")
        # print(summary_df.to_string())

        # Example scenario-level insights
        isFaster = np.nanmean(relative_change) < 0
        texts = []
        if isFaster:

            texts.append(
                f"Our approach uses up to {np.nanmax(fold_change)}-fold less {name[0]} compared to the baseline for {name[1]} using a multiplier of {name[2]}"
            )
            print(
                f"{name}\n"
                f"Our approach uses up to {np.nanmax(fold_change)}-fold less {name[0]} compared to the baseline for {name[1]} using a multiplier of {name[2]}"
            )
        else:
            texts.append(
                f"Our approach uses up to {np.nanmax(fold_change)}-fold more {name[0]} compared to the baseline for {name[1]} using a multiplier of {name[2]}"
            )
            print(
                f"{name}\n"
                f"Our approach uses up to {np.nanmax(fold_change)}-fold more {name[0]} compared to the baseline for {name[1]} using a multiplier of {name[2]}"
            )
        return stats, texts

    def run(self, data_naive, data_occp):
        time_data = self.create_scenario_lists(data_naive, data_occp, "avgTime")
        gas_data = self.create_scenario_lists(data_naive, data_occp, "avgGas")
        exp_data = self.create_scenario_lists(data_naive, data_occp, "avgExp")

        results = []  # {"time": {}, "gas": {}, "exp": {}}
        all_texts = []
        # results = {}
        for scenario in [
            "All",
            "HappyCase",
            "MaliciousUser",
            "LazyWorker_10",
            "LazyWorker_20",
            "LazyWorker_30",
            "LazyWorker_40",
        ]:
            for multiplier in ["all", "1", "10", "100", "1000"]:
                print(f"{scenario} stats:")
                stats, texts = self.calculate_stats(
                    ("Time", scenario, multiplier), time_data[scenario][multiplier]
                )
                all_texts.extend(texts)
                results.append({"key": f"time_{scenario}_{multiplier}", "stats": stats})
                stats, texts = self.calculate_stats(
                    ("Gas", scenario, multiplier), gas_data[scenario][multiplier]
                )
                all_texts.extend(texts)
                results.append({"key": f"gas_{scenario}_{multiplier}", "stats": stats})
                stats, texts = self.calculate_stats(
                    ("Expressions", scenario, multiplier),
                    exp_data[scenario][multiplier],
                )
                all_texts.extend(texts)
                results.append({"key": f"exp_{scenario}_{multiplier}", "stats": stats})
        return results, all_texts
