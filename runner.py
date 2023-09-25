import argparse
import sys

from runner.local_runner import LocalRunner
from runner.occp_runner import OCCPRunner


def main():
    parser = argparse.ArgumentParser(description='Parse an integer argument')
    parser.add_argument('--runtype', type=int, help='An integer argument')

    args = parser.parse_args()

    if args.runtype is not None:
        print(f"Received runtype: {args.runtype}")
    else:
        print("No runtype argument provided.")

    if args.runtype == 0:
        runner = LocalRunner()
    elif args.runtype == 1:
        runner = OCCPRunner()
    else:
        raise ValueError("Invalid run type")

    runner.run()


if __name__ == "__main__":
    sys.setrecursionlimit(2147483647)
    main()
