from postprocessing.commons import get_key_parts
import numpy as np


class Rq3GainsOverRq2:

    def __init__(self) -> None:
        pass

    def get_entry(self, data, key):
        for x in data:
            if x["key"] == key:
                return x
        return None

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
        fold_change = naive / ours  # ours / naive
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

    def run(self, data_rq3, data_rq2_time, data_rq2_gas):

        multiplier_1_data = [x for x in data_rq3 if get_key_parts(x["key"])[2] == "1"]
        time_100 = []
        gas_100 = []
        time_1000 = []
        gas_1000 = []
        max_time_100 = {"name": "", "value": 0}
        max_time_1000 = {"name": "", "value": 0}
        max_gas_100 = {"name": "", "value": 0}
        max_gas_1000 = {"name": "", "value": 0}
        for entry in multiplier_1_data:
            for step_size in ["100", "1000"]:
                prog, scen, _, _ = get_key_parts(entry["key"])
                key_time = f"{prog}_{step_size}_{scen}"
                key_gas = "_".join(entry["key"].split("_")[:-1]) + f"_{step_size}"
                entry_time = self.get_entry(data_rq2_time, key_time)
                entry_gas = self.get_entry(data_rq2_gas, key_gas)
                if entry_gas is None or entry_time is None:
                    continue
                if step_size == "100":
                    time_100.append((entry_time["average_cert"], entry["avgTime"]))
                    fold_inc = entry_time["average_cert"] / entry["avgTime"]
                    if fold_inc > max_time_100["value"]:
                        max_time_100["name"] = entry["key"]
                        max_time_100["value"] = fold_inc
                    fold_inc = (
                        np.round(
                            entry_gas["averages"]["total_costs"]["average"] / (10**6), 3
                        )
                        / entry["avgGas"]
                    )
                    if fold_inc > max_gas_100["value"]:
                        max_gas_100["name"] = entry["key"]
                        max_gas_100["value"] = fold_inc
                    gas_100.append(
                        (
                            np.round(
                                entry_gas["averages"]["total_costs"]["average"]
                                / (10**6),
                                3,
                            ),
                            entry["avgGas"],
                        )
                    )
                else:
                    time_1000.append((entry_time["average_cert"], entry["avgTime"]))
                    fold_inc = entry_time["average_cert"] / entry["avgTime"]
                    if fold_inc > max_time_1000["value"]:
                        max_time_1000["name"] = entry["key"]
                        max_time_1000["value"] = fold_inc
                    fold_inc = (
                        np.round(
                            entry_gas["averages"]["total_costs"]["average"] / (10**6), 3
                        )
                        / entry["avgGas"]
                    )
                    if fold_inc > max_gas_1000["value"]:
                        max_gas_1000["name"] = entry["key"]
                        max_gas_1000["value"] = fold_inc
                    gas_1000.append(
                        (
                            np.round(
                                entry_gas["averages"]["total_costs"]["average"]
                                / (10**6),
                                3,
                            ),
                            entry["avgGas"],
                        )
                    )

        print(f"Time 100: {max_time_100}")
        print(f"Time 1k: {max_time_1000}")
        print(f"Gas 100: {max_gas_100}")
        print(f"Gas 1k: {max_gas_1000}")
        results = []
        all_texts = []
        stat, texts = self.calculate_stats("Time_100", time_100)
        results.append({"Time100": stat})
        all_texts.extend(texts)
        stat, texts = self.calculate_stats("Gas_100", gas_100)
        results.append({"Gas100": stat})
        all_texts.extend(texts)

        stat, texts = self.calculate_stats("Time_1000", time_1000)
        results.append({"Time1000": stat})
        all_texts.extend(texts)
        stat, texts = self.calculate_stats("Gas_1000", gas_1000)
        results.append({"Gas1000": stat})
        all_texts.extend(texts)
        return results, all_texts
