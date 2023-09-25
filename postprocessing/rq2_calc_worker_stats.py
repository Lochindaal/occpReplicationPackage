import json
from tqdm import tqdm


class CalculateWorkerStatsRQ2:
    def __init__(self):
        self.result_file = './data/results/occp/worker_results.json'
        self.target_file = './data/results/occp/avg_worker_results.json'
        self.statement_sum = {}
        self.statement_count = {}
        self.workload_sum = {}
        self.workload_count = {}
        self.replay_sum = {}
        self.replay_count = {}
        self.vote_sum = {}
        self.vote_count = {}

    def compute_sum_count(self):
        # Read the JSON lines file
        with open(self.result_file, 'r') as file:
            for line in tqdm(file, desc='Computing sum and count'):
                try:
                    data = json.loads(line)
                except Exception as e:
                    print(line)
                    raise e

                parts = data['key'].split('_')
                key = '_'.join(parts[:-1])
                entry_type = data['Type']
                if entry_type == 'STMTS':
                    values = data['Statements']
                else:
                    values = data['Time']
                if key not in self.statement_sum:
                    self.statement_sum[key] = 0
                    self.statement_count[key] = 0
                    self.workload_sum[key] = 0
                    self.workload_count[key] = 0
                    self.vote_sum[key] = 0
                    self.vote_count[key] = 0
                    self.replay_sum[key] = 0
                    self.replay_count[key] = 0

                # Calculate and update the sum and count for each type
                if entry_type == "STMTS":
                    self.statement_sum[key] += values
                    self.statement_count[key] += 1
                if entry_type == "VOTE":
                    self.vote_sum[key] += values
                    self.vote_count[key] += 1
                if entry_type == "REPLAY":
                    self.replay_sum[key] += values
                    self.replay_count[key] += 1
                if entry_type == "WORKLOAD":
                    self.workload_sum[key] += values
                    self.workload_count[key] += 1

    def compute_average(self):
        averages = {}
        for key in tqdm(self.statement_sum.keys(), desc="Computing average"):
            averages[key] = {
                'avg_stmts': self.statement_sum[key] / 30,
                'avg_workload': self.workload_sum[key] / 30,
                'avg_replay': self.replay_sum[key] / 30,
                'avg_vote': self.vote_sum[key] / 30,
            }
        return averages

    def persist(self, averages):
        with open(self.target_file, 'w') as f:
            json.dump(averages, f, indent=3)

    def run(self):
        self.compute_sum_count()
        averages = self.compute_average()
        self.persist(averages)


def main():
    calc = CalculateWorkerStatsRQ2()
    calc.run()


if __name__ == "__main__":
    main()
