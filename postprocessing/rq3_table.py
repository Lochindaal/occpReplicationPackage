import os
from itertools import pairwise
from postprocessing.commons import load_data, load_data_line, write_to_jsonl


def get_prog(prog):
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


def get_scen(scen):
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


def add_latex_data(latex_data, program, scenario, approach, mult, gas, time, exp):
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


def get_key_parts(key):
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


def prepare_combined_data(approach_name, worker_data, gas_data, time_data):
    output_data = []
    latex_data = {}
    for entry in gas_data:
        entry_key = entry["key"]
        program, scenario, multiplier, step_size = get_key_parts(entry_key)
        if multiplier != "1":
            time_key = f"{program}_{multiplier}_{step_size}_{scenario}"
        else:
            time_key = f"{program}_{step_size}_{scenario}"

        cur_gas = entry["averages"]["total_costs"]["average"]
        cur_gas = round(cur_gas / 1e6, 3)
        time = time_data[time_key]["average_cert"]
        time = round(time, 3)
        exec_exp = worker_data[entry_key]["avg_stmts"]
        exec_exp = round(exec_exp, 3)

        output = {
            "key": entry_key,
            "avgGas": cur_gas,
            "avgExp": exec_exp,
            "avgTime": time,
        }

        add_latex_data(
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
    return output_data


def create_latex_table(path_to_table: str, input_data: dict) -> None:
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
                        prog_rows = f"\\multirow{{-{prog_counter+1}}}{{*}}{{ {get_prog(entry['prog'])}}}"
                        prog_counter = 0
                    if (
                        nextEntry["prog"] == entry["prog"]
                        and nextEntry["scenario"] == entry["scenario"]
                    ):
                        scenario_counter += 1
                        scen_rows = ""
                    else:
                        scen_rows = f"\\multirow{{-{scenario_counter+1}}}{{*}}{{ {get_scen(entry['scenario'])}}}"
                        scenario_counter = 0
                else:
                    is_last_prog = True
                    prog_rows = f"\\multirow{{-{prog_counter+1}}}{{*}}{{ {get_prog(entry['prog'])}}}"
                    scen_rows = f"\\multirow{{-{scenario_counter+1}}}{{*}}{{ {get_scen(entry['scenario'])}}}"
                    scenario_counter = 0
                    prog_counter = 0

                time_values = f"{entry["1"]['time']} & {entry["10"]['time']} & {entry["100"]['time']} & {entry["1000"]['time']}"
                gas_values = f"{entry["1"]['gas']} & {entry["10"]['gas']} & {entry["100"]['gas']} & {entry["1000"]['gas']}"
                exp_values = f"{entry["1"]['exp']} & {entry["10"]['exp']} & {entry["100"]['exp']} & {entry["1000"]['exp']}"
                table_entry = f"{prog_rows} & {scen_rows} & \\textsc{{{entry['approach']}}} & {time_values} & {gas_values} & {exp_values}\\\\\n"
                latex_file.write(table_entry)
                if is_last_prog:
                    latex_file.write("\\midrule\n")
            except Exception as ex:
                print(ex)


def main():

    base_path = "../data/"
    time_data_fpath = os.path.join(base_path, "results/avg_results.json")
    worker_data_fpath = os.path.join(base_path, "results/avg_worker_results.json")
    gas_data_fpath = os.path.join(base_path, "results/gas_costs.jsonl")
    combined_data_fpath = os.path.join(base_path, "output/combined_data.jsonl")
    latex_fpath = os.path.join(base_path, "output/rq3_table.tex")
    time_data = load_data(time_data_fpath)
    worker_data = load_data(worker_data_fpath)
    gas_data = load_data_line(gas_data_fpath)

    output_data, latex_data = prepare_combined_data(
        "OCCP", worker_data, gas_data, time_data
    )
    write_to_jsonl(combined_data_fpath, output_data)
    create_latex_table(latex_fpath, latex_data)


# output_data = []
# latex_data = {}
