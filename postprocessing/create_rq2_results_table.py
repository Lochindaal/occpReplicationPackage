import json

with open('./data/results/occp/avg_results.json', 'r') as f:
    data = json.load(f)

with open('./data/results/occp/avg_worker_results.json', 'r') as f:
    data_stmts = json.load(f)

# JSON data


# Initialize a list to hold the table data
table_data = []

# Define the header row
header = ["Program", "Scenario", "Stepsize = 100", "Stepsize = 1000", "Stepsize = 10000", "X", "Y"]

# Initialize a dictionary to collect data for each program
program_data = {}

# Iterate through the JSON data and extract program, scenario, and average_cert values
for key, value in data.items():
    parts = key.split("_")
    scenario = parts[-1]
    stepsize = parts[-2]
    program = parts[:-2]
    average_cert = value["average_cert"]

    # Create a unique key for each program
    program = '_'.join(program)
    program_key = f"{program}_{scenario}"

    # Initialize the program's data dictionary if not already done
    if program_key not in program_data:
        program_data[program_key] = {
            "Program": program_key,
            "Scenario": scenario,
            "Stepsize = 100": [],
            "Stepsize = 1000": [],
            "Stepsize = 10000": [],
            "Expressions100": [],
            "Expressions1000": [],
            "Expressions10000": [],
        }

    # Append data to the respective lists in the program's data dictionary
    # program_data[program_key]["Scenario"].append(scenario)
    program_data[program_key][f"Stepsize = {stepsize}"].append(average_cert)

for key, item in data_stmts.items():
    parts = key.split("_")
    scenario = parts[-2]
    stepsize = parts[-1]
    program = parts[:-2]
    numExpressions = round(item["avg_stmts"], 3)

    # Create a unique key for each program
    program = '_'.join(program)
    program_key = f"{program}_{scenario}"
    # print(f"{key}: {item}")
    program_data[program_key][f"Expressions{stepsize}"].append(numExpressions)


# Convert the program data to table rows
for program_key, program_row in program_data.items():
    # Combine multiple scenario entries into one string
    scenario_str = program_row["Scenario"]

    # Combine multiple average_cert entries into one string
    cert_100_str = ", ".join(map(str, program_row["Stepsize = 100"]))
    cert_1000_str = ", ".join(map(str, program_row["Stepsize = 1000"]))
    cert_10000_str = ", ".join(map(str, program_row["Stepsize = 10000"]))
    # Combine multiple expression entries into one string
    expr_100_str = ", ".join(map(str, program_row["Expressions100"]))
    expr_1000_str = ", ".join(map(str, program_row["Expressions1000"]))
    expr_10000_str = ", ".join(map(str, program_row["Expressions10000"]))
    # Append the row data to the table_data list
    table_data.append([
        program_row["Program"],
        scenario_str,
        cert_100_str,
        cert_1000_str,
        expr_100_str,
        expr_1000_str,
        expr_10000_str,
    ])


def get_scenario(scenario):
    match scenario:
        case "LazyWorker":
            return "\sclaz"
        case "MaliciousUser":
            return "\scmal"
        case "HappyCase":
            return "\schap"
        case "ERA":
            return "\scera"


def get_program_name(value):
    name = '_'.join(value.split('_')[:-1])
    match name:
        case "fibonacci":
            return "\\bpfib"
        case "fibonacci_iterative_pretty":
            return "\\bpfibi"
        case "merge_sort":
            return "\\bpmer"
        case "matrix_mul":
            return "\\bpmul"
        case "lanczos":
            return "\\bplaz"
        case "spf":
            return "\\bpspf"


# print(table_data)

def get_value(value):
    return value if value else 'TBD'

prog_name = ''
for entry in table_data:
    scenario = get_scenario(entry[1])
    name = get_program_name(entry[0])
    if name != prog_name:
        prog_name = name
        # print(f"\multirow{{4}}{{*}}{{{name}}} & {scenario} & {get_value(entry[2])} & {get_value(entry[3])}  & {get_value(entry[4])} & {get_value(entry[5])} \\\\")
        print(f"{name} & {scenario} & {get_value(entry[2])} & {get_value(entry[3])}  & {get_value(entry[4])} & {get_value(entry[5])} \\\\")
    else:
        print(f"& {scenario}  & {get_value(entry[2])} & {get_value(entry[3])}  & {get_value(entry[4])} & {get_value(entry[5])}\\\\")

# Generate the LaTeX table
# latex_table = tabulate(table_data, headers=header, tablefmt="latex_raw")
#
# # Print the LaTeX table
# print(latex_table)
