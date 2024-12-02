import os

import numpy as np
from tqdm import tqdm

from postprocessing.commons import get_key_parts, load_data_line, write_to_jsonl
from postprocessing.rq1_calc_average_results import CalculateAverageResultsRQ1
from postprocessing.rq2_calc_average_results import CalculateAverageResultsRQ2
from postprocessing.rq2_calc_gas_costs import CalculateGasCostsRQ2
from postprocessing.rq2_calc_worker_stats import CalculateWorkerStatsRQ2
from postprocessing.rq2_results_table import TableCreatorRQ2
from postprocessing.rq3_calc_results import Rq3CalculateResults
from postprocessing.rq3_comparison_rq2 import Rq3GainsOverRq2
from postprocessing.rq3_improvements import Rq3Improvements
from postprocessing.rq3_table import RQ3TableCreator


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
        write_to_jsonl(output_path, avg_time_data)
        avg_worker_data = CalculateWorkerStatsRQ2(worker_data_fpath).run()
        output_path = os.path.join(base_output_fpath, f"worker_data_{approach}.jsonl")
        write_to_jsonl(output_path, avg_worker_data)
        avg_gas_data = CalculateGasCostsRQ2(gas_data_fpath).run()
        output_path = os.path.join(base_output_fpath, f"gas_data_{approach}.jsonl")
        write_to_jsonl(output_path, avg_gas_data)


def compute_rq3_results():
    Rq3CalculateResults().run()
    RQ3TableCreator().create()


def rq3_compute_improvements():
    rq3_base_fp = "../data/rq3Data/processed"
    naive_data_fpath = os.path.join(rq3_base_fp, "combined_data_naive.jsonl")
    occp_data_fpath = os.path.join(rq3_base_fp, "combined_data_occp.jsonl")
    naive_data = load_data_line(naive_data_fpath)
    occp_data = load_data_line(occp_data_fpath)
    results, texts = Rq3Improvements().run(naive_data, occp_data)
    write_to_jsonl(os.path.join(rq3_base_fp, "stats.jsonl"), results)
    write_to_jsonl(os.path.join(rq3_base_fp, "texts.jsonl"), texts)
    print(results)


def rq3_compute_improvements_vs_rq2():
    rq2_base_fp = "../data/rq2Data/processed"
    rq3_base_fp = "../data/rq3Data/processed"

    rq2_time = load_data_line(os.path.join(rq2_base_fp, "time_data_occp.jsonl"))
    rq2_gas = load_data_line(os.path.join(rq2_base_fp, "gas_data_occp.jsonl"))
    rq3_data = load_data_line(os.path.join(rq3_base_fp, "combined_data_occp.jsonl"))

    results, texts = Rq3GainsOverRq2().run(rq3_data, rq2_time, rq2_gas)
    write_to_jsonl(os.path.join(rq3_base_fp, "stats_comp_rq2.jsonl"), results)
    write_to_jsonl(os.path.join(rq3_base_fp, "texts_comp_rq2.jsonl"), texts)
    print(results)


def compute_rq1_results():
    print("Executing post-processing for RQ1 (Results)")
    CalculateAverageResultsRQ1().run()


def main():
    computation_list = [
        (False, compute_rq1_results),
        (False, compute_rq2_results),
        (False, TableCreatorRQ2().run),
        (True, compute_rq3_results),
        (True, rq3_compute_improvements),
        (True, rq3_compute_improvements_vs_rq2),
    ]
    for do_compute, func in computation_list:
        if do_compute:
            func()
    print("Done.")


if __name__ == "__main__":
    main()
