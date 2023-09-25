import json

from protocol.eventListener.base_listener import BaseListener


class CertificationFailureListener(BaseListener):
    def __init__(self, listener_id, ecs, kill_all):
        event_filter = ecs.contract.events.TaskFailed.create_filter(fromBlock="latest")
        super().__init__(listener_id, ecs, kill_all, event_filter)

    def handle_event(self, event):
        event_json = json.loads(self.w3.to_json(event))
        task_id = event_json["args"]["taskId"]
        message = event_json["args"]["message"]
        self.logger.info(f"Task {task_id} failed to be certified ({message}).")
        self.loop_cond = False
