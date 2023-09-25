from postprocessing.rq1_calc_average_results import CalculateAverageResultsRQ1
from postprocessing.rq2_calc_average_results import CalculateAverageResultsRQ2
from postprocessing.rq2_calc_worker_stats import CalculateWorkerStatsRQ2


def main():
    post_proc_rq1 = CalculateAverageResultsRQ1()
    post_proc_rq2_1 = CalculateAverageResultsRQ2()
    post_proc_rq2_2 = CalculateWorkerStatsRQ2()

    print(f"Executing post-processing for RQ1 (Results)")
    post_proc_rq1.run()
    print(f"Executing post-processing for RQ2 (Results)")
    post_proc_rq2_1.run()
    print(f"Executing post-processing for RQ2 (Worker results)")
    post_proc_rq2_2.run()
    print(f"Done.")


if __name__ == "__main__":
    main()
