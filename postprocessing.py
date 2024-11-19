import os
import numpy as np
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


def main():

    rq2_base_fp = "../data/rq2Data"
    base_output_fpath = os.path.join(rq2_base_fp, "processed")

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

    work_data_naive = load_data_line(
        os.path.join(base_output_fpath, f"worker_data_naive.jsonl")
    )
    work_data_occp = load_data_line(
        os.path.join(base_output_fpath, f"worker_data_occp.jsonl")
    )

    avg_time_data_occp = compute_average_time("occp", work_data_occp)
    avg_time_data_naive = compute_average_time("naive", work_data_naive)
    persist(
        os.path.join(base_output_fpath, "avg_times_per_scenario_occp.jsonl"),
        avg_time_data_occp,
    )
    persist(
        os.path.join(base_output_fpath, "avg_times_per_scenario_naive.jsonl"),
        avg_time_data_naive,
    )

    for approach in ["naive", "occp"]:
        avgtps = load_data_line(
            os.path.join(base_output_fpath, f"avg_times_per_scenario_{approach}.jsonl")
        )
        results, increases = compute_increase(
            [
                "ERA",
                "HappyCase",
                "MaliciousUser",
                "LazyWorkerPercentage_10",
                "LazyWorkerPercentage_20",
                "LazyWorkerPercentage_30",
                "LazyWorkerPercentage_40",
            ],
            avgtps,
        )
        persist(os.path.join(base_output_fpath, f"increases_{approach}.jsonl"), results)
        persist2(
            os.path.join(base_output_fpath, f"increases_avg_{approach}.jsonl"),
            increases,
        )

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
