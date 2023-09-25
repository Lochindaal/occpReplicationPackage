import json
from tqdm import tqdm


class CalculateAverageResultsRQ2:
    def __init__(self):
        self.result_file = './data/results/occp/results.json'
        self.target_file = './data/results/occp/avg_results.json'
        self.execution_sum = {}
        self.execution_count = {}

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

                    # Calculate and update the sum and count for each type
                    self.execution_sum[key] += sum(times)
                    self.execution_count[key] += len(times)

    def compute_average(self):
        averages = {}
        for key in tqdm(self.execution_sum.keys(), desc='Computing average'):
            averages[key] = {
                'average_cert': round(self.execution_sum[key] / self.execution_count[key], 3),
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
    calc = CalculateAverageResultsRQ2()
    calc.run()


if __name__ == "__main__":
    main()
