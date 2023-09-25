import json
import os
import random
import sys
import time
from abc import ABC
from threading import Event

from protocol.storage.data_storage import DataStorage
from protocol.user.user_factory import UserFactory
from protocol.user.user_type import UserType
from protocol.utils.ecs_utils import init_ecs
from protocol.utils.fs_utils import delete_directory, save_json_lines
from protocol.utils.node_utils import initialize_nodes
from runner.base_runner import BaseRunner
from runner.experiment_scenarios import ExperimentScenarios


class OCCPRunner(BaseRunner, ABC):
    def __init__(self):
        super().__init__(2)
        self.address_list = self.load_address_list()
        self.reruns = int(self.config["EXPERIMENT"]["NumberReruns"])
        assert self.reruns <= len(self.address_list)
        # self.logger = init_logger()

    @staticmethod
    def load_address_list():
        with open("./data/ecs/contract_list.dat") as handler:
            contract_data = handler.readlines()
        contract_list = list(map(lambda line: line.strip("\n"), contract_data))
        return contract_list

    def delete_worker_directories(self):
        num_seq = self.config.getint("NODES", "Sequencers")
        base_path = os.path.join(self.config["EXPERIMENT"]["DumpDir"], "occp")
        for i in range(num_seq):
            del_dir = os.path.join(base_path, f"node{i}")
            delete_directory(del_dir)

    def get_scenarios(self, run_single_test):
        if run_single_test:
            scenarios = [ExperimentScenarios.Config]
        else:
            # ToDo: Execute one scenario after the other. Blockchain get bloated with data and reduces speed
            # ToDo: write function to remove data after certificate was issued or malicious actioins have been found!
            scenarios = [
                ExperimentScenarios.HappyCase,
                ExperimentScenarios.LazyWorker,
                ExperimentScenarios.MaliciousUser,
                # ExperimentScenarios.ERA,
            ]
        return scenarios

    def execute_experiments(self, program_list):
        # Fetch configuration values outside the loops
        program_base_dir = self.config["EXPERIMENT"]["ProgramBaseDir"]
        run_single_test = self.config.getboolean("EXPERIMENT", "RunSingleTest")
        steps = json.loads(self.config["EXPERIMENT"]["StepsOccp"])

        # Create a list of scenarios based on the configuration
        scenarios = self.get_scenarios(run_single_test)
        results = []
        for key in program_list:
            program_path = os.path.join(program_base_dir, f"{key}.mona")
            for step in steps:
                for scenario in scenarios:
                    self.delete_worker_directories()
                    run_args = {
                        "key": key,
                        "program_path": program_path,
                        "steps": step,
                        "scenario": scenario,
                    }
                    run_time = self.execute_reruns(run_args)
                    result = {f"{key}_{step}_{scenario.name}": run_time}
                    results.append(result)
                    path = os.path.join(self.base_path, "occp", "results.json")
                    save_json_lines(result, path)
        return results

    def execute_rerunsNew(self, run_args):
        reruns = int(self.config["EXPERIMENT"]["NumberReruns"])
        exec_times = [self.execute_run(run, run_args) for run in range(reruns)]
        return exec_times

    def execute_reruns(self, run_args):
        reruns = int(self.config["EXPERIMENT"]["NumberReruns"])
        exec_times = []
        for run in range(reruns):
            exec_times.append(self.execute_run(run, run_args))
            self.write_execution_time(run, run_args, exec_times)
        return exec_times

    def write_execution_time(self, run_id, run_args, exec_times):
        key = f"{run_args['key']}_{run_args['steps']}_{run_args['scenario'].name}_{run_id}"
        output = {key: exec_times}
        path = os.path.join(self.base_path, "occp", "results_partial.json")
        save_json_lines(output, path)

    def execute_run(self, run_id, run_args):
        self.delete_worker_directories()
        run_args["run_id"] = run_id
        reruns = self.config.getint("EXPERIMENT", "NumberReruns")
        # self.delete_worker_directories()
        # run_args["run_id"] = run_id
        self.logger.info(
            f"Starting {run_args['scenario'].name} for {run_args['key']} "
            f"(Run {run_id + 1}/{reruns})"
        )

        start_time = time.time()
        # init ecs lib
        base_address = self.config['NETWORK']['BCBaseAddress']
        ecs_list = [
            init_ecs(f"{base_address}:{i}0002", self.address_list[run_id])
            for i in range(1, 4)
        ]

        # create user
        user_type = self.get_user_type(run_args)
        if user_type == UserType.ERA:
            run_args["alt_code"] = "fibonacci_iterative_era"
        user = UserFactory().create_user(user_type, ecs_list[0], run_args)
        task_data = user.run()
        # start up all nodes
        kill_all = Event()

        node_data = {
            "ecs_list": ecs_list,
            "task_list": [task_data],
            "kill_event": kill_all,
        }
        # ToDo: include run_args in initialization to overwrite the config file!
        # ToDo: check if ThreadPoolExecutor makes more sense!
        (
            sequencer_nodes,
            certifier_nodes,
            verifier_nodes,
            lazy_worker_node,
        ) = initialize_nodes(node_data, run_args)

        if run_args['scenario'] == ExperimentScenarios.LazyWorker:
            first_to_start = [lazy_worker_node, random.choice(certifier_nodes)]
            random.shuffle(first_to_start)
            [x.start() for x in first_to_start]
            lazy_worker_node.join()

        [thread.start() for thread in certifier_nodes if not thread.is_alive()]

        [t.join() for t in verifier_nodes]
        end_time = time.time() - start_time
        kill_all.set()
        if lazy_worker_node is not None:
            lazy_worker_node.join()
        [t.join() for t in certifier_nodes]
        [t.join() for t in sequencer_nodes]
        return end_time

    def get_user_type(self, run_args):
        scenario = run_args["scenario"]
        if scenario == ExperimentScenarios.Config:
            user_type = UserType(self.config.getint("MALICIOUS", "User"))
        else:
            match scenario:
                case ExperimentScenarios.MaliciousUser:
                    user_type = UserType.Malicious
                case ExperimentScenarios.ERA:
                    user_type = UserType.ERA
                case _:
                    user_type = UserType.Normal
        return user_type

    def run(self):
        program_list = json.loads(self.config["EXPERIMENT"]["ProgramsOccp"])
        DataStorage("ecs").create_bucket()
        self.execute_experiments(program_list)
