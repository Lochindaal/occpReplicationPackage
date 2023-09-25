import random
from threading import Thread

from protocol.eventListener.CertificationFailureListener import (
    CertificationFailureListener,
)
from protocol.eventListener.CertificationSuccessListener import (
    CertificationSuccessListener,
)
from protocol.eventListener.Sequencer import Sequencer
from protocol.eventListener.listener_type import ListenerType
from protocol.utils.config_utils import load_config
from protocol.worker.base_worker import ClientType
from protocol.worker.malicious.malicious_worker import MaliciousWorker
from protocol.worker.normal.normal_worker import NormalWorker
from runner.experiment_scenarios import ExperimentScenarios


def start_worker(worker_id, ecs, kill_all, run_args, client_type: ClientType):
    if client_type == ClientType.NORMAL:
        node = NormalWorker(worker_id, ecs, kill_all, run_args)
    else:
        node = MaliciousWorker(worker_id, ecs, kill_all, run_args)
    t = Thread(target=node.run)
    # t.start()
    return t


def start_workers(n_workers, data, run_args, client_type: ClientType, reserved_ids=[]):
    worker_nodes = []
    for worker_id in range(n_workers):
        if worker_id in reserved_ids:
            continue
        ecs_node = worker_id % len(data["ecs_list"])
        ecs = data["ecs_list"][ecs_node]
        kill_event = data["kill_event"]
        worker_nodes.append(start_worker(worker_id, ecs, kill_event, run_args, client_type))
    return worker_nodes


def create_listener(listener_id, data, listener_type: ListenerType):
    ecs_node = listener_id % len(data["ecs_list"])
    ecs = data["ecs_list"][ecs_node]
    kill_event = data["kill_event"]
    match listener_type:
        case ListenerType.SEQUENCER:
            node = Sequencer(listener_id, ecs, kill_event)
        case ListenerType.CERT_FAILURE:
            node = CertificationFailureListener(listener_id, ecs, kill_event)
        case ListenerType.CERT_SUCCESS:
            node = CertificationSuccessListener(
                listener_id, ecs, kill_event, random.choice(data["task_list"])
            )
        case _:
            raise AttributeError(f"No listener type found for {listener_type}")
    t = Thread(target=node.run)
    return t


def start_listeners(n_listeners, data, listener_type: ListenerType):
    listener_nodes = []
    for n in range(n_listeners):
        t = create_listener(n, data, listener_type)
        listener_nodes.append(t)
        t.start()
    return listener_nodes


def initialize_nodes(data, run_args):
    config = load_config()
    mal_config = config["MALICIOUS"]
    node_config = config["NODES"]

    lazy_worker_id = -1
    lazy_worker_node = None
    scenario = run_args["scenario"]
    if (
            scenario == ExperimentScenarios.Config and mal_config.getboolean("Worker")
    ) or scenario == ExperimentScenarios.LazyWorker:
        lazy_worker_id = random.randint(1, 5)
        lazy_worker_node = start_worker(
            lazy_worker_id,
            data["ecs_list"][0],
            data["kill_event"],
            run_args,
            ClientType.MALICIOUS,
        )

    sequencer_nodes = start_listeners(
        node_config.getint("Sequencers"), data, ListenerType.SEQUENCER
    )

    certifier_nodes = start_workers(
        node_config.getint("Certifiers"),
        data,
        run_args,
        ClientType.NORMAL,
        reserved_ids=[lazy_worker_id],
    )

    if (
            mal_config.getint("User") != 1 and scenario == ExperimentScenarios.Config
    ) or scenario in (ExperimentScenarios.MaliciousUser, ExperimentScenarios.ERA):
        listener_type = ListenerType.CERT_FAILURE
    else:
        listener_type = ListenerType.CERT_SUCCESS
    # listener_type = ListenerType.CERT_SUCCESS if mal_config.getint("User") == 1 else ListenerType.CERT_FAILURE
    verifier_nodes = start_listeners(
        node_config.getint("Verifiers"), data, listener_type
    )

    return sequencer_nodes, certifier_nodes, verifier_nodes, lazy_worker_node
