import json
import os
import pickle
import time
from abc import ABC
from enum import Enum

import numpy as np

from protocol.utils.fs_utils import create_directory, save_json_lines, delete_directory
from runner.base_runner import BaseRunner, RunType


class MeasurementType(Enum):
    EXECUTION = "execution"
    RECORDING = "recording"
    REPLAY = "replay"


class LocalRunner(BaseRunner, ABC):
    def __init__(self):
        super().__init__(2)

    def run(self):
        program_list = json.loads(self.config["EXPERIMENT"]["Programs"])
        results = self.execute_experiments(program_list)
        result_path = os.path.join(
            self.base_path, self.config["DATA"]["LocalResultDir"], "local_results.pickle"
        )
        with open(result_path, "wb") as handler:
            pickle.dump(results, handler)

    @staticmethod
    def add_to_result(result, step, value, measure_type: MeasurementType):
        if step not in result.keys():
            result.update({step: {"execution": [], "recording": [], "replay": []}})

        result[step][measure_type.value].extend(value)

    def execute_reruns(self, program, step, run_type: RunType):
        reruns = int(self.config["EXPERIMENT"]["NumberReruns"])
        base_dump_dir = self.config["EXPERIMENT"]["DumpDir"]
        key, path = program
        dump_dir = os.path.join(base_dump_dir, f"{key}_{step}")
        # create_directory(dump_dir)
        time_list = []
        # print(f"Recording {key} with {step} steps")
        for run in range(reruns):
            if run_type != RunType.RUN_REPLAY:
                delete_directory(dump_dir)
                create_directory(dump_dir)
            start_time = time.time()
            self.execute_program(path, run_type, dump_dir=dump_dir, steps=step)
            time_list.append(time.time() - start_time)
        return time_list

    def execute_experiments(self, program_list):
        result_path = os.path.join(
            self.base_path, self.config["DATA"]["LocalResultDir"], "local_results.json"
        )
        results = {}
        steps = json.loads(self.config["EXPERIMENT"]["Steps"])
        for key in program_list:
            path = os.path.join(
                self.config["EXPERIMENT"]["ProgramBaseDir"], f"{key}.mona"
            )
            result = {}
            self.logger.info(f"Executing {key}")
            run_time = self.execute_reruns((key, path), 0, RunType.RUN)
            self.logger.info(f"TIME: {np.average(run_time)}")
            for step in steps:
                step_result = {
                    f"{key}_{step}": 1
                }
                # run
                self.add_to_result(result, step, run_time, MeasurementType.EXECUTION)
                # record
                self.logger.info(f"Recording {key} with {step}")
                recording_time = self.execute_reruns(
                    (key, path), step, RunType.RUN_RECORD
                )
                self.add_to_result(
                    result, step, recording_time, MeasurementType.RECORDING
                )
                self.logger.info(f"TIME: {np.average(recording_time)}")
                # replay
                self.logger.info(f"Replaying {key} with {step}")
                replay_time = self.execute_reruns((key, path), step, RunType.RUN_REPLAY)
                self.add_to_result(result, step, replay_time, MeasurementType.REPLAY)
                self.logger.info(f"TIME: {np.average(replay_time)}")
                # Open the JSONLines file for writing (append mode)
                step_result[f"{key}_{step}"] = result[step]
                save_json_lines(step_result, result_path)
            if key not in results.keys():
                results.update({key: result})
            else:
                results[key] = result
        return results
