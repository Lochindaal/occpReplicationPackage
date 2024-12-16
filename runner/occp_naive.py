import json
import os
import random
import subprocess
import time
from abc import ABC
from threading import Event

from naive.node_utils_naive import initialize_nodes
from naive.user import User
from protocol.storage.data_storage import DataStorage
from protocol.user.user_type import UserType
from protocol.utils.ecs_utils import init_ecs
from protocol.utils.fs_utils import delete_directory, save_json_lines
from runner.base_runner import BaseRunner
from runner.experiment_scenarios import ExperimentScenarios


class OCCPNaive(BaseRunner, ABC):
    def __init__(self, program, step_size):
        super().__init__(2, "occp_naive.ini")
        self.program = program
        self.step_size = step_size
        self.address_list = self.load_address_list()
        self.reruns = int(self.config["EXPERIMENT"]["NumberReruns"])
        assert self.reruns <= len(self.address_list)

    @staticmethod
    def load_address_list():
        with open("./data/ecs/contract_list_naive.dat") as handler:
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
            scenarios = [
                ExperimentScenarios.HappyCase,
                ExperimentScenarios.MaliciousUser,
                ExperimentScenarios.LazyWorkerPercentage_10,
                ExperimentScenarios.LazyWorkerPercentage_20,
                ExperimentScenarios.LazyWorkerPercentage_30,
                ExperimentScenarios.LazyWorkerPercentage_40,
                ExperimentScenarios.ERA,
            ]
        return scenarios

    def restart_container(self):
        # restart docker container
        container_name = "polygon-container"
        command = ["docker", "restart", container_name]
        try:
            # Run the command and wait for it to complete
            self.logger.info(f"Container '{container_name}' restarting...")
            subprocess.run(command, check=True)
            time.sleep(10)
            self.logger.info(f"Container '{container_name}' restarted successfully.")
        except subprocess.CalledProcessError as e:
            self.logger.info(f"Error restarting container '{container_name}': {e}")
        except FileNotFoundError:
            self.logger.info("Docker is not installed or not in PATH.")

    def execute_experiments_informed(self, program_list):
        # Fetch configuration values outside the loops
        program_base_dir = self.config["EXPERIMENT"]["ProgramBaseDir"]
        run_single_test = self.config.getboolean("EXPERIMENT", "RunSingleTest")
        steps = [self.step_size]

        # Create a list of scenarios based on the configuration
        scenarios = self.get_scenarios(run_single_test)
        results = []
        for key, step in zip(program_list, steps):
            program_path = os.path.join(program_base_dir, f"{key}.mona")
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
                self.restart_container()
        return results

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
                    if scenario == ExperimentScenarios.ERA:
                        if key != "fibonacci":
                            continue
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

    def execute_reruns(self, run_args):
        # define the command as a list of arguments
        command = [
            "aws",
            "--endpoint-url=http://localhost:4566",
            "s3",
            "rm",
            "s3://ecs",
            "--recursive",
        ]
        reruns = int(self.config["EXPERIMENT"]["NumberReruns"])
        exec_times = []
        for run in range(reruns):
            # Execute the command
            self.logger.info("Cleaning S3 storage.")
            subprocess.run(command, text=True)
            self.logger.info("Cleaning S3 storage ended.")
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
        self.logger.info(
            f"Starting {run_args['scenario'].name} for {run_args['key']} "
            f"(Run {run_id + 1}/{reruns})"
        )

        start_time = time.time()
        # init ecs lib
        base_address = self.config["NETWORK"]["BCBaseAddress"]
        ecs_list = [
            init_ecs(
                f"{base_address}:{i}0002",
                self.address_list[run_id],
                run_args=run_args,
                is_naive=True,
            )
            for i in range(1, 4)
        ]

        # create user
        user_type = self.get_user_type(run_args)
        if user_type == UserType.ERA:
            run_args["alt_code"] = "fibonacci_iterative_era"
        user = User(user_type, ecs_list[0], run_args)
        task_data = user.run()
        # start up all nodes
        kill_all = Event()

        node_data = {
            "ecs_list": ecs_list,
            "task_list": [task_data],
            "kill_event": kill_all,
        }
        # ToDo: check if ThreadPoolExecutor makes more sense!
        (
            certifier_nodes,
            verifier_nodes,
            lazy_worker_nodes,
        ) = initialize_nodes(node_data, run_args)

        if run_args["scenario"] in (
            ExperimentScenarios.LazyWorker,
            ExperimentScenarios.LazyWorkerPercentage,
            ExperimentScenarios.LazyWorkerPercentage_10,
            ExperimentScenarios.LazyWorkerPercentage_20,
            ExperimentScenarios.LazyWorkerPercentage_30,
            ExperimentScenarios.LazyWorkerPercentage_40,
        ):
            first_to_start = lazy_worker_nodes + certifier_nodes
            random.shuffle(first_to_start)
            [x.start() for x in first_to_start]

        [thread.start() for thread in certifier_nodes if not thread.is_alive()]
        [t.join() for t in verifier_nodes]
        if len(lazy_worker_nodes) > 0:
            [x.join() for x in lazy_worker_nodes]
        [t.join() for t in certifier_nodes]
        end_time = time.time() - start_time
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
        program_list = [self.program]
        isInformed = self.config.getboolean("EXPERIMENT", "IsInformedSteps")
        DataStorage("ecs").create_bucket()
        if isInformed:
            self.execute_experiments_informed(program_list)
        else:
            self.execute_experiments(program_list)
