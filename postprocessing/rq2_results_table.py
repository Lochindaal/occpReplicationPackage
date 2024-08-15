from tqdm import tqdm
import jsonlines


class TableCreatorRQ2:
    def __init__(self):
        self.path_gas = "./data/results/occp/gas_costs.jsonl"
        self.path_worker = "./data/results/occp/avg_worker_results.jsonl"
        self.path_time = "./data/results/occp/avg_results.jsonl"
        self.target_file = "./data/results/occp/table_entries.tex"

        self.entries = {}

    def load_input_data(self, path):
        data = []
        counter = 0
        with jsonlines.open(path) as reader:
            for obj in reader:
                data.append(obj)
                counter += 1
        return data

    def process_results(self, data, entry_key, target_key, process_name):
        for entry in tqdm(data, desc=f"Processing {process_name} data"):
            key = entry["key"]
            parts = key.split("_")

            is_lazyWorker_entry = "LazyWorkerPercentage" in key
            len_scenario = 2 if is_lazyWorker_entry else 1

            if process_name == "time":
                scenario = "_".join(parts[-(len_scenario):])
                step_size = parts[-(len_scenario + 1)]
                program = "_".join(parts[: -(len_scenario + 1)])
            else:
                step_size = parts[-1]
                scenario = "_".join(parts[-(len_scenario + 1) : -1])
                program = "_".join(parts[: -(len_scenario + 1)])

            #                results.jsonl
            #                prog step scenario

            # prog scen step
            # {"key": "matrix_mul_MaliciousUser_100", "averages": {"total_costs": {"average": 587358508.6, "average_formatted": 587.359, "mean": 323429.36543014995}, "add_task": {"average": 198172.0, "average_formatted": 0.198, "mean": 198172.0}, "add_traces": {"average": 289285723.0, "average_formatted": 289.286, "mean": 6574675.5227272725}, "vote": {"average": 177820658.6, "average_formatted": 177.821, "mean": 204626.76478711164}, "get_workload": {"average": 33529354.0, "average_formatted": 33.529, "mean": 37294.89525786956}, "upload_sequence": {"average": 86524601.0, "average_formatted": 86.525, "mean": 28841533.666666668}, "upload_conflicts": {"average": 0.0, "average_formatted": 0.0, "mean": 0.0}}}
            # {"key": "lanczos_LazyWorkerPercentage_10_100", "averages": {"total_costs": {"average": 640154497.5666667, "average_formatted": 640.154, "mean": 381597.05380809505}, "add_task": {"average": 174772.0, "average_formatted": 0.175, "mean": 174772.0}, "add_traces": {"average": 253972230.0, "average_formatted": 253.972, "mean": 6512108.461538462}, "vote": {"average": 160700753.9, "average_formatted": 160.701, "mean": 203212.89061709662}, "get_workload": {"average": 30771856.066666666, "average_formatted": 30.772, "mean": 37386.83306334035}, "upload_sequence": {"average": 193371889.1, "average_formatted": 193.372, "mean": 12422177.029978586}, "upload_conflicts": {"average": 1162996.5, "average_formatted": 1.163, "mean": 142991.37295081967}}}

            # avg_worker.jsonl
            # prog scen step
            # {"key": "matrix_mul_MaliciousUser_100", "avg_stmts": 86781.0, "avg_workload": 2835.3286003112794, "avg_replay": 145.72035590012868, "avg_vote": 2774.5590076526005}
            # {"key": "lanczos_LazyWorkerPercentage_10_100", "avg_stmts": 78514.66666666667, "avg_workload": 2695.6524268627168, "avg_replay": 157.95984338919322, "avg_vote": 2598.1067761262257}

            new_key = f"{program}_{scenario}"  # "_".join(parts[:-2])
            if new_key not in self.entries:
                self.entries[new_key] = {
                    "key": new_key,
                    "program": program,
                    "scenario": scenario,
                    "tex_entry": "",
                    "time_100": 0,
                    "statements_100": 0,
                    "gas_100": 0,
                    "time_1000": 0,
                    "statements_1000": 0,
                    "gas_1000": 0,
                }
            cur_target_key = f"{target_key}_{step_size}"
            if process_name == "gas":
                if "merge" in key and is_lazyWorker_entry:
                    print("FUBAR")
                self.entries[new_key][cur_target_key] = entry["averages"][
                    "total_costs"
                ][entry_key]
            else:
                self.entries[new_key][cur_target_key] = entry[entry_key]

    def persist(self, data):
        with jsonlines.open(self.target_file, mode="w") as writer:
            writer.write_all(data)

    def run(self):
        gas_data = self.load_input_data(self.path_gas)
        worker_data = self.load_input_data(self.path_worker)
        time_data = self.load_input_data(self.path_time)

        self.process_results(time_data, "average_cert", "time", "time")
        self.process_results(worker_data, "avg_stmts", "statements", "statements")
        self.process_results(gas_data, "average_formatted", "gas", "gas")

        prepared_data = []
        for key, entry in tqdm(self.entries.items()):
            prog_key = ""
            scen_key = ""
            match entry["program"]:
                case "fibonacci_iterative_pretty":
                    prog_key = "\\bpfibi"
                case "fibonacci":
                    prog_key = "\\bpfib"
                case "matrix_mul":
                    prog_key = "\\bpmat"
                case "merge_sort":
                    prog_key = "\\bpmer"
                case "lanczos":
                    prog_key = "\\bplaz"
                case "spf":
                    prog_key = "\\bpspf"
            match entry["scenario"]:
                case "HappyCase":
                    scen_key = "\\schap"
                case "MaliciousUser":
                    scen_key = "\\scmal"
                case (
                    "LazyWorkerPercentage_10"
                    | "LazyWorkerPercentage_20"
                    | "LazyWorkerPercentage_30"
                    | "LazyWorkerPercentage_40"
                ):
                    prts = entry["scenario"].split("_")
                    scen_key = f"\\sclaz {prts[1]}\\%"
                case "ERA":
                    scen_key = "\\scera"

            if prog_key == "" or scen_key == "":
                print("FUBAR!")
                continue

            entry["tex_entry"] = (
                f"{prog_key} & {scen_key} & {entry['time_100']} & {entry['time_1000']} & {entry['gas_100']} & {entry['gas_1000']} & {entry['statements_100']} & {entry['statements_1000']} & baseline_3 & baseline_20 \\"
            )
            prepared_data.append(entry)
        self.persist(prepared_data)


# def main():
#    calc = CalculateWorkerStatsRQ2()
#    calc.run()
#
#
# if __name__ == "__main__":
#    main()
