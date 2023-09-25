import json
import time

from protocol.eventListener.base_listener import BaseListener
from protocol.sequence.sequence_analyzer import SequenceAnalyzer


class Sequencer(BaseListener):
    def __init__(self, listener_id, ecs, kill_all):
        event_filter = ecs.contract.events.VoteForSequenceRequested.create_filter(
            fromBlock="latest"
        )
        super().__init__(listener_id, ecs, kill_all, event_filter)
        self.analyzer = SequenceAnalyzer()

    def handle_event(self, event):
        event_json = json.loads(self.w3.to_json(event))
        task_id = event_json["args"]["taskId"]
        task_sequences = self.ecs.get_sequence_data(task_id)
        conflicts, pos_sequence = self.analyzer.run(task_sequences)
        if len(conflicts) > 0:
            self.logger.info(f"Sequencer {self.listener_id} found conflicts")
            self.logger.info(conflicts)
            receipt, tx_hash = self.ecs.upload_conflicts(task_id, conflicts, self.listener_id)
            retry_counter = 1
            while receipt.status != 1 and retry_counter < 5:
                retry_counter += 1
                time.sleep(1)
                receipt, tx_hash = self.ecs.upload_conflicts(task_id, conflicts, self.listener_id)
        else:
            self.logger.info(f"Sequencer {self.listener_id} found possible sequence")
            self.logger.info(pos_sequence)
            receipt, tx_hash = self.ecs.upload_sequence(
                task_id, pos_sequence, self.listener_id
            )
            retry_counter = 1
            while receipt.status != 1 and retry_counter < 5:
                retry_counter += 1
                time.sleep(1)
                receipt, tx_hash = self.ecs.upload_sequence(
                    task_id, pos_sequence, self.listener_id
                )
