from postprocessing.rq1_calc_average_results import CalculateAverageResultsRQ1
from postprocessing.rq2_calc_average_results import CalculateAverageResultsRQ2
from postprocessing.rq2_calc_worker_stats import CalculateWorkerStatsRQ2
from postprocessing.rq2_calc_gas_costs import CalculateGasCostsRQ2
import subprocess


def main():
    post_proc_rq1 = CalculateAverageResultsRQ1()
    post_proc_rq2_1 = CalculateAverageResultsRQ2()
    post_proc_rq2_2 = CalculateWorkerStatsRQ2()
    post_proc_rq2_3 = CalculateGasCostsRQ2()

    print("Executing post-processing for RQ1 (Results)")
    post_proc_rq1.run()
    print("Executing post-processing for RQ2 (Results)")
    post_proc_rq2_1.run()
    print("Executing post-processing for RQ2 (Worker results)")
    post_proc_rq2_2.run()
    print("Executing post-processing for RQ2 (Transaction costs)")
    # Prepare combined transaction log
    command = 'find ./data/results/occp/ -type f -name "transaction_log.json" -exec cat {} + > ./data/results/occp/all_transaction_logs.jsonl'
    subprocess.run(command, shell=True, check=True)
    # Calculate avarage costs
    post_proc_rq2_3.run()
    print("Done.")


if __name__ == "__main__":
    main()
