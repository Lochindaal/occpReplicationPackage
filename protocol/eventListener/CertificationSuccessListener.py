import json
import time

from protocol.eventListener.base_listener import BaseListener


class CertificationSuccessListener(BaseListener):
    def __init__(self, listener_id, ecs, kill_all, data):
        self.data = data
        event_filter = ecs.contract.events.CertificateCreated.create_filter(
            fromBlock="latest"
        )
        super().__init__(listener_id, ecs, kill_all, event_filter)

    def handle_event(self, event):
        event_json = json.loads(self.w3.to_json(event))
        task_id = event_json["args"]["taskId"]
        # cert_id = event_json["args"]["certId"]
        code = self.data["payload"]["source_loc"]
        input_hash = self.data["payload"]["input_hash"]
        target_hash = self.data["payload"]["target_hash"]

        start_time = time.time()
        cert = self.ecs.get_certificate(code, input_hash, target_hash)
        self.logger.debug(
            f"Search certificate request took {(time.time() - start_time)} seconds"
        )
        if cert[0] > 0:
            self.loop_cond = False
            self.logger.info(
                f"Verifier {self.listener_id} found certificate for Task {task_id}"
                f"\n\tCodeHash: {cert[2]}"
                f"\n\tSequenceHash: {cert[3]}"
                f"\n\tCertHash: {cert[4]}"
            )
