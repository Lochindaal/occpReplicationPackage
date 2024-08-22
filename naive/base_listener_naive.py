import asyncio
import logging
from abc import abstractmethod

from protocol.utils.config_utils import load_config
from protocol.utils.web3_utils import init_web3_connection, Web3ProviderType


class BaseListener:
    def __init__(self, listener_id, ecs, kill_all, event_filter_template, filter_type):
        self.listener_id = listener_id
        self.config = load_config()
        self.ecs = ecs
        self.kill_all = kill_all
        self.filter_type = filter_type
        self.event_filter_template = event_filter_template
        self.poll_interval = self.config.getint("NODES", "PollInterval")
        self.w3 = init_web3_connection(
            Web3ProviderType.Socket, self.config["NETWORK"]["WebSocket"]
        )
        self.loop_cond = True
        self.logger = logging.getLogger(self.config["LOGGING"]["LogName"])

    def run(self):
        event_filter = self.filter_type.create_filter(fromBlock="latest")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                asyncio.gather(self.log_loop(event_filter, self.poll_interval))
            )
        finally:
            loop.close()

    # asynchronous defined function to loop
    # this loop sets up an event filter and is looking for new entries for the "VoteForSequenceRequested" event
    # this loop runs on a poll interval
    async def log_loop(self, event_filter, poll_interval):
        while not self.kill_all.isSet() and self.loop_cond:
            try:
                events = self.filter_type.get_logs(fromBlock="latest")
                for event in events:
                    self.handle_event(event)
            except Exception as e:
                if "filter not found" in str(e).lower():
                    print("Recreating filter due to filter not found")
                    event_filter = self.filter_type.create_filter(fromBlock="latest")
                print(e)

            await asyncio.sleep(poll_interval)

    @abstractmethod
    def handle_event(self, event):
        pass
