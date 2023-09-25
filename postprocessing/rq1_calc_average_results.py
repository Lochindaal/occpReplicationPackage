import json
from tqdm import tqdm


class CalculateAverageResultsRQ1:

    def __init__(self):
        self.result_file = './data/results/local/local_results.json'
        self.target_file = './data/results/local/avg_results.json'
        # Initialize dictionaries to store the sum and count for each key
        self.execution_sum = {}
        self.execution_count = {}
        self.recording_sum = {}
        self.recording_count = {}
        self.replay_sum = {}
        self.replay_count = {}

    def compute_sum_count(self):
        # Read the JSON lines file
        with open(self.result_file, 'r') as file:
            for line in tqdm(file, desc="Computing sum and count"):
                data = json.loads(line)

                # Iterate through each key in the JSON object
                for key, times in data.items():
                    if key not in self.execution_sum:
                        self.execution_sum[key] = 0
                        self.execution_count[key] = 0
                        self.recording_sum[key] = 0
                        self.recording_count[key] = 0
                        self.replay_sum[key] = 0
                        self.replay_count[key] = 0

                    # Calculate and update the sum and count for each type
                    self.execution_sum[key] += sum(times['execution'])
                    self.execution_count[key] += len(times['execution'])
                    self.recording_sum[key] += sum(times['recording'])
                    self.recording_count[key] += len(times['recording'])
                    self.replay_sum[key] += sum(times['replay'])
                    self.replay_count[key] += len(times['replay'])

    def compute_average(self):
        # Calculate the average for each key
        averages = {}
        for key in tqdm(self.execution_sum.keys(), desc='Computing average'):
            averages[key] = {
                'average_execution': self.execution_sum[key] / self.execution_count[key],
                'average_recording': self.recording_sum[key] / self.recording_count[key],
                'average_replay': self.replay_sum[key] / self.replay_count[key]
            }
        return averages

    def persist(self, averages):
        # json_data = json.dumps(averages)
        with open(self.target_file, 'w') as f:
            json.dump(averages, f, indent=3)

    def run(self):
        self.compute_sum_count()
        averages = self.compute_average()
        self.persist(averages)


def main():
    calc = CalculateAverageResultsRQ1()
    calc.run()

if __name__ == "__main__":
    main()

