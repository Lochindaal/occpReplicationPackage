import os
import math
from itertools import pairwise
from postprocessing.commons import load_data, load_data_line, write_to_jsonl


class RQ3TableCreator:
    def __init__(self) -> None:
        pass

    def get_prog(self, prog):
        match prog.lower():
            case "fibonacci":
                return "\\bpfib"
            case "fibonacci_iterative_pretty":
                return "\\bpfibi"
            case "spf":
                return "\\bpspf"
            case "lanczos":
                return "\\bplaz"
            case "merge_sort":
                return "\\bpmer"
            case "matrix_mul":
                return "\\bpmat"
        return prog

    def get_scen(self, scen):
        match scen.lower():
            case "happycase":
                return "\\schap"
            case "malicioususer":
                return "\\scmal"
            case "lazyworker":
                return "\\sclaz"
        if "lazyworker" in scen.lower():
            return f"\\sclaz {scen.split('_')[1]}\\%"
        return scen

    def add_latex_data(
        self, latex_data, program, scenario, approach, mult, gas, time, exp
    ):
        key = f"{approach}_{program}_{scenario}"
        if key not in latex_data:
            latex_data[key] = {
                "prog": program,
                "scenario": scenario,
                "approach": approach,
                mult: {"gas": gas, "time": time, "exp": exp},
            }
        else:
            if mult not in latex_data[key]:
                latex_data[key][mult] = {"gas": gas, "time": time, "exp": exp}

    def get_key_parts(self, key):
        key_parts = key.split("_")
        step_size = key_parts[-1]

        if key_parts[-2].isnumeric():
            scenario = "_".join(key_parts[-3:-1])
            if key_parts[-4].isnumeric():
                multiplier = key_parts[-4]
                program = "_".join(key_parts[:-4])
            else:
                multiplier = "1"
                program = "_".join(key_parts[:-3])
        else:
            scenario = key_parts[-2]
            if key_parts[-3].isnumeric():
                multiplier = key_parts[-3]
                program = "_".join(key_parts[:-3])
            else:
                multiplier = "1"
                program = "_".join(key_parts[:-2])
        return program, scenario, multiplier, step_size

    def get_entry_with_key(self, entries, key):
        for x in entries:
            if x["key"] == key:
                return x
        return None

    def prepare_combined_data(self, approach_name, worker_data, gas_data, time_data):
        output_data = []
        latex_data = {}
        for entry in gas_data:
            try:
                entry_key = entry["key"]
                program, scenario, multiplier, step_size = self.get_key_parts(entry_key)
                if multiplier != "1":
                    time_key = f"{program}_{multiplier}_{step_size}_{scenario}"
                else:
                    time_key = f"{program}_{step_size}_{scenario}"

                cur_gas = entry["averages"]["total_costs"]["average"]
                cur_gas = round(cur_gas / 1e6, 3)
                time = self.get_entry_with_key(time_data, time_key)["average_cert"]
                time = round(time, 3)
                exec_exp = self.get_entry_with_key(worker_data, entry_key)["avg_stmts"]
                exec_exp = round(exec_exp, 3)

                output = {
                    "key": entry_key,
                    "avgGas": cur_gas,
                    "avgExp": exec_exp,
                    "avgTime": time,
                }

                self.add_latex_data(
                    latex_data,
                    program,
                    scenario,
                    approach_name,
                    multiplier,
                    cur_gas,
                    time,
                    exec_exp,
                )
                output_data.append(output)
            except Exception as ex:
                print(ex)
        return output_data, latex_data

    def create_latex_table(self, path_to_table: str, input_data: dict) -> None:
        with open(path_to_table, "a") as latex_file:
            prog_counter = 0
            scenario_counter = 0
            is_last_prog = False
            sorted_data = dict(
                sorted(
                    input_data.items(),
                    key=lambda item: (
                        item[1]["prog"],
                        item[1]["scenario"],
                        item[1]["approach"],
                    ),
                )
            )
            sorted_data["END"] = {"prog": "END", "scenario": "END", "approach": "END"}
            for (_, entry), (_, nextEntry) in pairwise(sorted_data.items()):
                try:
                    prog_rows = ""
                    scen_rows = ""
                    if nextEntry:
                        if nextEntry["prog"] == entry["prog"]:
                            prog_counter += 1
                            is_last_prog = False
                            prog_rows = ""
                        else:
                            is_last_prog = True
                            prog_rows = f"\\multirow{{-{prog_counter+1}}}{{*}}{{ {self.get_prog(entry['prog'])}}}"
                            prog_counter = 0
                        if (
                            nextEntry["prog"] == entry["prog"]
                            and nextEntry["scenario"] == entry["scenario"]
                        ):
                            scenario_counter += 1
                            scen_rows = ""
                        else:
                            scen_rows = f"\\multirow{{-{scenario_counter+1}}}{{*}}{{ {self.get_scen(entry['scenario'])}}}"
                            scenario_counter = 0
                    else:
                        is_last_prog = True
                        prog_rows = f"\\multirow{{-{prog_counter+1}}}{{*}}{{ {self.get_prog(entry['prog'])}}}"
                        scen_rows = f"\\multirow{{-{scenario_counter+1}}}{{*}}{{ {self.get_scen(entry['scenario'])}}}"
                        scenario_counter = 0
                        prog_counter = 0

                    # time_values = f"{entry["1"]['time']} & {entry["10"]['time']} & {entry["100"]['time']} & {entry["1000"]['time']}"
                    # gas_values = f"{entry["1"]['gas']} & {entry["10"]['gas']} & {entry["100"]['gas']} & {entry["1000"]['gas']}"
                    # exp_values = f"{entry["1"]['exp']} & {entry["10"]['exp']} & {entry["100"]['exp']} & {entry["1000"]['exp']}"
                    time_values = f"{entry["1"]['time']} & {self.get_value(entry, "10", "time",0)} & {self.get_value(entry, "100", "time",0)}& {self.get_value(entry, "1000", "time",0)}"
                    gas_values = f"{entry["1"]['gas']} & {self.get_value(entry, "10", "gas",0)} & {self.get_value(entry, "100", "gas",0)}& {self.get_value(entry, "1000", "gas",0)}"
                    exp_values = f"{self.get_value(entry,"1","exp",-6)} & {self.get_value(entry, "10", "exp",-6)} & {self.get_value(entry, "100", "exp",-6)}& {self.get_value(entry, "1000", "exp",-6)}"
                    table_entry = f"{prog_rows} & {scen_rows} & \\textsc{{{entry['approach']}}} & {time_values} & {gas_values} & {exp_values}\\\\\n"
                    latex_file.write(table_entry)
                    if is_last_prog:
                        latex_file.write("\\midrule\n")
                except Exception as ex:
                    print(ex)

    def get_value(self, entry, key1, key2, div):
        try:
            value = entry[key1][key2]
            value = value * math.pow(10, div)
            value = round(value, 3)
        except Exception as ex:
            print(f"Value for {key1}{key2} could not be extracted.\n\t{ex}")
            value = 0
        return value

    def create(self):
        base_path = "../data/rq3Data/processed"

        latex_data = {}
        latex_fpath = os.path.join(base_path, "rq3_table.tex")
        for approach in ["naive", "occp"]:
            time_data_fpath = os.path.join(base_path, f"time_data_{approach}.jsonl")
            worker_data_fpath = os.path.join(base_path, f"worker_data_{approach}.jsonl")
            gas_data_fpath = os.path.join(base_path, f"gas_data_{approach}.jsonl")
            combined_data_fpath = os.path.join(
                base_path, f"combined_data_{approach}.jsonl"
            )
            time_data = load_data_line(time_data_fpath)
            worker_data = load_data_line(worker_data_fpath)
            gas_data = load_data_line(gas_data_fpath)

            output_data, latex_data_approach = self.prepare_combined_data(
                approach, worker_data, gas_data, time_data
            )
            latex_data.update(latex_data_approach)
            write_to_jsonl(combined_data_fpath, output_data)
        self.create_latex_table(latex_fpath, latex_data)


# def main():
#
#    base_path = "../data/rq3Data/processed"
#
#    latex_data = {}
#    latex_fpath = os.path.join(base_path, "rq3_table.tex")
#    for approach in ["naive", "occp"]:
#        time_data_fpath = os.path.join(base_path, f"time_data_{approach}.jsonl")
#        worker_data_fpath = os.path.join(base_path, f"worker_data_{approach}.jsonl")
#        gas_data_fpath = os.path.join(base_path, f"gas_data_{approach}.jsonl")
#        combined_data_fpath = os.path.join(base_path, f"combined_data_{approach}.jsonl")
#        time_data = load_data(time_data_fpath)
#        worker_data = load_data(worker_data_fpath)
#        gas_data = load_data_line(gas_data_fpath)
#
#        output_data, latex_data_approach = prepare_combined_data(
#            approach, worker_data, gas_data, time_data
#        )
#        latex_data.update(latex_data_approach)
#        write_to_jsonl(combined_data_fpath, output_data)
#    create_latex_table(latex_fpath, latex_data)


# output_data = []
# latex_data = {}
