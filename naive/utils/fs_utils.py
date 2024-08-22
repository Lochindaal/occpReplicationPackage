import os
import shutil

from jsonlines import jsonlines


def save_json_lines(lines, path):
    with jsonlines.open(path, mode="a") as writer:
        writer.write(lines)

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def delete_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
