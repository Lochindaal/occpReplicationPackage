import jsonlines
import json


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


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def load_data_line(path):
    data = []
    with jsonlines.open(path, "r") as reader:
        for obj in reader:
            data.append(obj)
    return data


def write_to_jsonl(path, data):
    with jsonlines.open(path, mode="w") as writer:
        writer.write_all(data)
