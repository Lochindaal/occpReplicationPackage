import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import json
import jsonlines
from postprocessing.commons import get_key_parts, load_data_line
from postprocessing.rq1_calc_average_results import CalculateAverageResultsRQ1
from postprocessing.rq2_calc_average_results import CalculateAverageResultsRQ2
from postprocessing.rq2_calc_worker_stats import CalculateWorkerStatsRQ2
from postprocessing.rq2_calc_gas_costs import CalculateGasCostsRQ2
from postprocessing.rq2_results_table import TableCreatorRQ2
import subprocess

# import pandas as pd
from postprocessing.rq3_improvements import Rq3Improvements
from postprocessing.rq3_table import RQ3TableCreator
from postprocessing.rq3_calc_results import Rq3CalculateResults


def persist(output_path, data):
    with jsonlines.open(output_path, mode="w") as writer:
        writer.write_all(data)


def persist2(output_path, data):
    with jsonlines.open(output_path, mode="w") as writer:
        writer.write(data)


def compute_increase(scenario_list, avg_time_data_per_scen):
    data = []

    increases = {
        "avg_workload_perc": 0,
        "avg_workload_times": 0,
        "avg_vote_perc": 0,
        "avg_vote_times": 0,
        "workload_perc": [],
        "vote_perc": [],
        "workload_times": [],
        "vote_times": [],
    }

    for scenario in scenario_list:

        data_100 = [d for d in avg_time_data_per_scen if d["key"] == f"{scenario}_100"][
            0
        ]
        data_1000 = [
            d for d in avg_time_data_per_scen if d["key"] == f"{scenario}_1000"
        ][0]

        workload_calls_100 = data_100["mean_workload_call"]
        workload_calls_1000 = data_1000["mean_workload_call"]
        vote_calls_100 = data_100["mean_vote_call"]
        vote_calls_1000 = data_1000["mean_vote_call"]

        data.append(
            {
                "key": scenario,
                "increase_workload": 100 / workload_calls_1000 * workload_calls_100,
                "increase_vote": 100 / vote_calls_1000 * vote_calls_100,
                "increase_workload_times": workload_calls_100 * workload_calls_1000,
                "increase_vote_times": vote_calls_100 / vote_calls_1000,
            }
        )
        increases["workload_perc"].append(
            100 / workload_calls_1000 * workload_calls_100
        )
        increases["vote_perc"].append(100 / vote_calls_1000 * vote_calls_100)
        increases["workload_times"].append(workload_calls_100 * workload_calls_1000)
        increases["vote_times"].append(vote_calls_100 / vote_calls_1000)

    increases["avg_workload_perc"] = np.mean(increases["workload_perc"])
    increases["avg_workload_times"] = np.mean(increases["workload_times"])
    increases["avg_vote_perc"] = np.mean(increases["vote_perc"])
    increases["avg_vote_times"] = np.mean(increases["vote_times"])
    return data, increases


def compute_average_time(approach: str, work_data):
    sum_100_vote = {}
    sum_1000_vote = {}

    for line in tqdm(work_data, desc="Computing overheads"):
        program, scenario, multiplier, step_size = get_key_parts(line["key"])
        new_key = f"{scenario}_{step_size}"
        workload_time = line["avg_workload"] / line["avg_workload_count"]
        vote_time = line["avg_vote"] / line["avg_vote_count"]
        if step_size == "100":
            if new_key in sum_100_vote:
                sum_100_vote[new_key]["vote_time"].append(vote_time)
                sum_100_vote[new_key]["workload_time"].append(workload_time)
                sum_100_vote[new_key]["call_count_vote"].append(line["avg_vote_count"])
                sum_100_vote[new_key]["call_count_workload"].append(
                    line["avg_workload_count"]
                )

            else:
                sum_100_vote[new_key] = {
                    "vote_time": [vote_time],
                    "workload_time": [workload_time],
                    "call_count_vote": [line["avg_vote_count"]],
                    "call_count_workload": [line["avg_workload_count"]],
                }
        else:
            if new_key in sum_100_vote:
                sum_1000_vote[new_key]["vote_time"].append(vote_time)
                sum_1000_vote[new_key]["workload_time"].append(workload_time)
                sum_1000_vote[new_key]["call_count_vote"].append(line["avg_vote_count"])
                sum_1000_vote[new_key]["call_count_workload"].append(
                    line["avg_workload_count"]
                )
            else:
                sum_1000_vote[new_key] = {
                    "vote_time": [vote_time],
                    "workload_time": [workload_time],
                    "call_count_vote": [line["avg_vote_count"]],
                    "call_count_workload": [line["avg_workload_count"]],
                }
    data = []
    for key, value in sum_100_vote.items():
        mean_vote_time = np.mean(value["vote_time"])
        mean_workload_time = np.mean(value["workload_time"])
        mean_workload_call = np.mean(value["call_count_workload"])
        mean_vote_call = np.mean(value["call_count_vote"])
        data.append(
            {
                "key": key,
                "mean_vote_time": round(mean_vote_time, 3),
                "mean_workload_time": round(mean_workload_time, 3),
                "mean_workload_call": round(mean_workload_call, 3),
                "mean_vote_call": round(mean_vote_call, 3),
            }
        )
    for key, value in sum_1000_vote.items():
        mean_vote_time = np.mean(value["vote_time"])
        mean_workload_time = np.mean(value["workload_time"])
        mean_workload_call = np.mean(value["call_count_workload"])
        mean_vote_call = np.mean(value["call_count_vote"])
        data.append(
            {
                "key": key,
                "mean_vote_time": round(mean_vote_time, 3),
                "mean_workload_time": round(mean_workload_time, 3),
                "mean_workload_call": round(mean_workload_call, 3),
                "mean_vote_call": round(mean_vote_call, 3),
            }
        )

    return data


def compute_rq2_results():
    rq2_base_fp = "../data/rq2Data"
    base_output_fpath = os.path.join(rq2_base_fp, "processed")

    for approach in ["naive", "occp"]:
        time_data_fpath = os.path.join(rq2_base_fp, approach, "results.jsonl")
        gas_data_fpath = os.path.join(rq2_base_fp, approach, "transaction_logs.jsonl")
        worker_data_fpath = os.path.join(rq2_base_fp, approach, "worker_results.jsonl")
        base_output_fpath = os.path.join(rq2_base_fp, "processed")

        avg_time_data = CalculateAverageResultsRQ2(time_data_fpath).run()
        output_path = os.path.join(base_output_fpath, f"time_data_{approach}.jsonl")
        persist(output_path, avg_time_data)
        avg_worker_data = CalculateWorkerStatsRQ2(worker_data_fpath).run()
        output_path = os.path.join(base_output_fpath, f"worker_data_{approach}.jsonl")
        persist(output_path, avg_worker_data)
        avg_gas_data = CalculateGasCostsRQ2(gas_data_fpath).run()
        output_path = os.path.join(base_output_fpath, f"gas_data_{approach}.jsonl")
        persist(output_path, avg_gas_data)


def compute_rq3_results():
    Rq3CalculateResults().run()
    RQ3TableCreator().create()


def get_entry(key, data):
    for entry in data:
        if entry["key"] == key:
            return entry
    return None


def calculate_stats(data):
    stats = {
        "all": {},
        "1": {},
        "10": {},
        "100": {},
        "1000": {},
    }
    for x in ["all", "1", "10", "100", "1000"]:
        y = {
            "mean": np.mean(data[x]),
            "variance": np.var(data[x], ddof=1),  # Sample variance
            "median": np.median(data[x]),
            "min": np.min(data[x]) if len(data[x]) > 0 else 0,
            "max": np.max(data[x]) if len(data[x]) > 0 else 0,
        }
        stats[x] = y
    return stats


def append_multiplier(multiplier, key1, key2, data, entry_naive, entry_ours):
    match multiplier:
        case "1":
            data[key1]["1"].append(entry_naive[key2] - entry_ours[key2])
        case "10":
            data[key1]["10"].append(entry_naive[key2] - entry_ours[key2])
        case "100":
            data[key1]["100"].append(entry_naive[key2] - entry_ours[key2])
        case "1000":
            data[key1]["1000"].append(entry_naive[key2] - entry_ours[key2])


def add_entry(data, entry_naive, entry_ours, key1, key2, multiplier):
    data[key1]["all"].append(entry_naive[key2] - entry_ours[key2])
    append_multiplier(multiplier, key1, key2, data, entry_naive, entry_ours)

    naive = entry_naive[key2]
    ours = entry_ours[key2]
    # Relative increase/decrease in percentage
    relative_change = (ours - naive) / naive * 100  # In percentage
    # relative_change[naive == 0] = np.nan  # Handle division by zero cases
    data[f"{key1}_rel"]["all"].append(relative_change)
    append_multiplier(multiplier, f"{key1}_rel", key2, data, entry_naive, entry_ours)
    # Magnitude increase/decrease
    magnitude_change = np.abs(ours - naive)
    data[f"{key1}_mag"]["all"].append(magnitude_change)
    append_multiplier(multiplier, f"{key1}_mag", key2, data, entry_naive, entry_ours)
    # Fold increase/decrease
    fold_change = ours / naive
    # fold_change[naive == 0] = ( np.inf)  # Handle division by zero cases (infinite fold change)
    data[f"{key1}_fold"]["all"].append(magnitude_change)
    append_multiplier(multiplier, f"{key1}_fold", key2, data, entry_naive, entry_ours)


## Summary statistics for analysis
# stats = {
#    "Mean Relative Change (%)": np.nanmean(relative_change),
#    "Median Relative Change (%)": np.nanmedian(relative_change),
#    "Min Relative Change (%)": np.nanmin(relative_change),
#    "Max Relative Change (%)": np.nanmax(relative_change),
#    "Mean Magnitude Change": np.nanmean(magnitude_change),
#    "Median Magnitude Change": np.nanmedian(magnitude_change),
#    "Mean Fold Change": np.nanmean(fold_change),
#    "Median Fold Change": np.nanmedian(fold_change)
# }
#
## Convert to DataFrame for better representation
# summary_df = pd.DataFrame([stats])
#
## Print results
# print("Summary Statistics:")
# print(summary_df)
#
## Example scenario-level insights
# scenario_level = {
#    "Scenario 1 - Mean Fold Change": np.nanmean(fold_change[0]),
#    "Scenario 1 - Median Fold Change": np.nanmedian(fold_change[0]),
#    "Scenario 1 - Max Magnitude Change": np.nanmax(magnitude_change[0]),
# }
# print("\nScenario 1 Insights:")
# print(scenario_level)
#    data[f"{key1}_det"].append(
#        {
#            "key": entry_ours["key"],
#            f"{key1}_diff": entry_naive[key2] - entry_ours[key2],
#        }
#    )


def calculate_stats2(data: list[tuple[float, float]]):
    # Relative increase/decrease in percentage
    naive = np.array([x[0] for x in data])
    ours = np.array([x[1] for x in data])
    relative_change = (ours - naive) / naive * 100  # In percentage
    relative_change[naive == 0] = np.nan  # Handle division by zero cases

    # Magnitude increase/decrease
    magnitude_change = np.abs(ours - naive)

    # Fold increase/decrease
    fold_change = ours / naive
    fold_change[naive == 0] = (
        np.inf
    )  # Handle division by zero cases (infinite fold change)

    # Summary statistics for analysis
    stats = {
        "Mean Relative Change (%)": np.nanmean(relative_change),
        "Median Relative Change (%)": np.nanmedian(relative_change),
        "Min Relative Change (%)": np.nanmin(relative_change),
        "Max Relative Change (%)": np.nanmax(relative_change),
        "Mean Magnitude Change": np.nanmean(magnitude_change),
        "Median Magnitude Change": np.nanmedian(magnitude_change),
        "Min Magnitude Change (%)": np.nanmin(magnitude_change),
        "Max Magnitude Change (%)": np.nanmax(magnitude_change),
        "Mean Fold Change": np.nanmean(fold_change),
        "Median Fold Change": np.nanmedian(fold_change),
        "Min Fold Change (%)": np.nanmin(fold_change),
        "Max Fold Change (%)": np.nanmax(fold_change),
    }

    # Convert to DataFrame for better representation
    summary_df = pd.DataFrame([stats])

    # Print results
    print("Summary Statistics:")
    print(summary_df.to_string())

    # Example scenario-level insights
    scenario_level = {
        "Scenario 1 - Mean Fold Change": np.nanmean(fold_change[0]),
        "Scenario 1 - Median Fold Change": np.nanmedian(fold_change[0]),
        "Scenario 1 - Max Magnitude Change": np.nanmax(magnitude_change[0]),
    }
    print("\nScenario 1 Insights:")
    print(scenario_level)


def rq3_compute_average_increases():
    rq3_base_fp = "../data/rq3Data/processed"
    naive_data_fpath = os.path.join(rq3_base_fp, "combined_data_naive.jsonl")
    occp_data_fpath = os.path.join(rq3_base_fp, "combined_data_occp.jsonl")
    naive_data = load_data_line(naive_data_fpath)
    occp_data = load_data_line(occp_data_fpath)
    step_size_naive = "100000000000"

    increase_eval = {
        "stats": {
            "time": {},
            "gas": {},
            "exp": {},
        },
        "time": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "time_rel": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "time_mag": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "time_fold": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "exp": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "exp_rel": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "exp_mag": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "exp_fold": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "gas": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "gas_rel": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "gas_mag": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "gas_fold": {"1": [], "10": [], "100": [], "1000": [], "all": []},
        "exp_det": [],
        "time_det": [],
        "gas_det": [],
    }

    increase_mult = {
        "all": {"gas": [], "time": [], "exp": []},
        "1": {"gas": [], "time": [], "exp": []},
        "10": {"gas": [], "time": [], "exp": []},
        "100": {"gas": [], "time": [], "exp": []},
        "1000": {"gas": [], "time": [], "exp": []},
    }
    for entry in occp_data:
        key_parts = entry["key"].split("_")
        _, _, multiplier, _ = get_key_parts(entry["key"])
        naive_key = "_".join(key_parts[:-1]) + f"_{step_size_naive}"
        naive_entry = get_entry(naive_key, naive_data)
        if naive_entry is None:
            continue

        increase_mult["all"]["time"].append((naive_entry["avgTime"], entry["avgTime"]))
        increase_mult["all"]["exp"].append((naive_entry["avgExp"], entry["avgExp"]))
        increase_mult["all"]["gas"].append((naive_entry["avgGas"], entry["avgGas"]))
        increase_mult[multiplier]["time"].append(
            (naive_entry["avgTime"], entry["avgTime"])
        )
        increase_mult[multiplier]["exp"].append(
            (naive_entry["avgExp"], entry["avgExp"])
        )
        increase_mult[multiplier]["gas"].append(
            (naive_entry["avgGas"], entry["avgGas"])
        )
        add_entry(increase_eval, naive_entry, entry, "time", "avgTime", multiplier)
        add_entry(increase_eval, naive_entry, entry, "exp", "avgExp", multiplier)
        add_entry(increase_eval, naive_entry, entry, "gas", "avgGas", multiplier)

    print("\n------ 100 --------\n")
    print("      Time:")
    calculate_stats2(increase_mult["100"]["time"])
    print("      Gas:")
    calculate_stats2(increase_mult["100"]["gas"])
    print("      Exp:")
    calculate_stats2(increase_mult["100"]["exp"])
    print("\n------ 10 --------\n")
    print("      Time:")
    calculate_stats2(increase_mult["10"]["time"])
    print("      Gas:")
    calculate_stats2(increase_mult["10"]["gas"])
    print("      Exp:")
    calculate_stats2(increase_mult["10"]["exp"])

    # increase_eval["stats"]["time"] = calculate_stats(increase_eval["time"])
    # increase_eval["stats"]["gas"] = calculate_stats(increase_eval["gas"])
    # increase_eval["stats"]["exp"] = calculate_stats(increase_eval["exp"])
    # increase_eval["stats"]["time_rel"] = calculate_stats(increase_eval["time_rel"])
    # increase_eval["stats"]["gas_rel"] = calculate_stats(increase_eval["gas_rel"])
    # increase_eval["stats"]["exp_rel"] = calculate_stats(increase_eval["exp_rel"])
    return increase_eval


def rq3_compute_improvements():
    rq3_base_fp = "../data/rq3Data/processed"
    naive_data_fpath = os.path.join(rq3_base_fp, "combined_data_naive.jsonl")
    occp_data_fpath = os.path.join(rq3_base_fp, "combined_data_occp.jsonl")
    naive_data = load_data_line(naive_data_fpath)
    occp_data = load_data_line(occp_data_fpath)
    results = Rq3Improvements().run(naive_data, occp_data)
    persist(os.path.join(rq3_base_fp, "stats.jsonl"), results)
    print(results)


def main():
    compute_rq2_results()
    compute_rq3_results()
    rq3_compute_improvements()

    # rq2_base_fp = "../data/rq2Data"
    # base_output_fpath = os.path.join(rq2_base_fp, "processed")
    # work_data_naive = load_data_line(
    #    os.path.join(base_output_fpath, f"worker_data_naive.jsonl")
    # )
    # work_data_occp = load_data_line(
    #    os.path.join(base_output_fpath, f"worker_data_occp.jsonl")
    # )
    # avg_time_data = compute_average_time("occp", work_data_occp)
    # persist(
    #    os.path.join(base_output_fpath, "avg_times_per_scenario.jsonl"), avg_time_data
    # )

    # for approach in ["naive", "occp"]:
    #    time_data_fpath = os.path.join(rq2_base_fp, approach, "results.jsonl")
    #    gas_data_fpath = os.path.join(rq2_base_fp, approach, "transaction_logs.jsonl")
    #    worker_data_fpath = os.path.join(rq2_base_fp, approach, "worker_results.jsonl")
    #    base_output_fpath = os.path.join(rq2_base_fp, "processed")

    #    avg_time_data = CalculateAverageResultsRQ2(time_data_fpath).run()
    #    output_path = os.path.join(base_output_fpath, f"time_data_{approach}.jsonl")
    #    persist(output_path, avg_time_data)
    #    avg_worker_data = CalculateWorkerStatsRQ2(worker_data_fpath).run()
    #    output_path = os.path.join(base_output_fpath, f"worker_data_{approach}.jsonl")
    #    persist(output_path, avg_worker_data)
    #    avg_gas_data = CalculateGasCostsRQ2(gas_data_fpath).run()
    #    output_path = os.path.join(base_output_fpath, f"gas_data_{approach}.jsonl")
    #    persist(output_path, avg_gas_data)

    # work_data_naive = load_data_line(
    #    os.path.join(base_output_fpath, f"worker_data_naive.jsonl")
    # )
    # work_data_occp = load_data_line(
    #    os.path.join(base_output_fpath, f"worker_data_occp.jsonl")
    # )

    # avg_time_data_occp = compute_average_time("occp", work_data_occp)
    # avg_time_data_naive = compute_average_time("naive", work_data_naive)
    # persist(
    #    os.path.join(base_output_fpath, "avg_times_per_scenario_occp.jsonl"),
    #    avg_time_data_occp,
    # )
    # persist(
    #    os.path.join(base_output_fpath, "avg_times_per_scenario_naive.jsonl"),
    #    avg_time_data_naive,
    # )

    # for approach in ["naive", "occp"]:
    #    avgtps = load_data_line(
    #        os.path.join(base_output_fpath, f"avg_times_per_scenario_{approach}.jsonl")
    #    )
    #    results, increases = compute_increase(
    #        [
    #            "ERA",
    #            "HappyCase",
    #            "MaliciousUser",
    #            "LazyWorkerPercentage_10",
    #            "LazyWorkerPercentage_20",
    #            "LazyWorkerPercentage_30",
    #            "LazyWorkerPercentage_40",
    #        ],
    #        avgtps,
    #    )
    #    persist(os.path.join(base_output_fpath, f"increases_{approach}.jsonl"), results)
    #    persist2(
    #        os.path.join(base_output_fpath, f"increases_avg_{approach}.jsonl"),
    #        increases,
    #    )

    # post_proc_rq1 = CalculateAverageResultsRQ1()
    # post_proc_rq2_1 = CalculateAverageResultsRQ2()
    # post_proc_rq2_2 = CalculateWorkerStatsRQ2()
    # post_proc_rq2_3 = CalculateGasCostsRQ2()
    # post_proc_rq2_4 = TableCreatorRQ2()

    # print("Executing post-processing for RQ1 (Results)")
    # post_proc_rq1.run()
    # print("Executing post-processing for RQ2 (Results)")
    # post_proc_rq2_1.run()
    # print("Executing post-processing for RQ2 (Worker results)")
    # post_proc_rq2_2.run()
    # print("Executing post-processing for RQ2 (Transaction costs)")
    ## Prepare combined transaction log
    # command = 'find ./data/results/occp/ -type f -name "transaction_log.json" -exec cat {} + > ./data/results/occp/all_transaction_logs.jsonl'
    # subprocess.run(command, shell=True, check=True)
    ## Calculate avarage costs
    # post_proc_rq2_3.run()
    ### Create tex ready format
    # post_proc_rq2_4.run()
    print("Done.")


if __name__ == "__main__":
    main()
