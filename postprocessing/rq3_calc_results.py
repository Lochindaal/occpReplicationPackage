import os

from postprocessing.commons import write_to_jsonl
from postprocessing.rq2_calc_average_results import CalculateAverageResultsRQ2
from postprocessing.rq2_calc_worker_stats import CalculateWorkerStatsRQ2
from postprocessing.rq2_calc_gas_costs import CalculateGasCostsRQ2


class Rq3CalculateResults:
    def __init__(self) -> None:
        pass

    def run(self):
        print("START")
        rq3_base_fp = "../data/rq3Data"
        base_output_fpath = os.path.join(rq3_base_fp, "processed")
        for approach in ["naive", "occp"]:
            time_data_fpath = os.path.join(rq3_base_fp, approach, "results.jsonl")
            gas_data_fpath = os.path.join(
                rq3_base_fp, approach, "transaction_logs.jsonl"
            )
            worker_data_fpath = os.path.join(
                rq3_base_fp, approach, "worker_results.jsonl"
            )
            base_output_fpath = os.path.join(rq3_base_fp, "processed")

            avg_time_data = CalculateAverageResultsRQ2(time_data_fpath).run()
            output_path = os.path.join(base_output_fpath, f"time_data_{approach}.jsonl")
            write_to_jsonl(output_path, avg_time_data)
            avg_worker_data = CalculateWorkerStatsRQ2(worker_data_fpath).run()
            output_path = os.path.join(
                base_output_fpath, f"worker_data_{approach}.jsonl"
            )
            write_to_jsonl(output_path, avg_worker_data)
            avg_gas_data = CalculateGasCostsRQ2(gas_data_fpath).run()
            output_path = os.path.join(base_output_fpath, f"gas_data_{approach}.jsonl")
            write_to_jsonl(output_path, avg_gas_data)
