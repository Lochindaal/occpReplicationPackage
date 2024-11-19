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
    work_data_naive = load_data_line(
        os.path.join(base_output_fpath, f"worker_data_naive.jsonl")
    )
    work_data_occp = load_data_line(
        os.path.join(base_output_fpath, f"worker_data_occp.jsonl")
    )
    avg_time_data = compute_average_time("occp", work_data_occp)
    persist(
        os.path.join(base_output_fpath, "avg_times_per_scenario.jsonl"), avg_time_data
    )

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
