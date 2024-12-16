#!/bin/bash

# Define the array of X values
#tuples=( "fibonacci" "fibonacci_iterative_pretty" "lanczos" "spf" "merge_sort" "matrix_mul" "fibonacci_10" "fibonacci_iterative_pretty_10" "lanczos_10" "spf_10" "merge_sort_10" "matrix_mul_10" "fibonacci_100" "fibonacci_iterative_pretty_100" "lanczos_100" "spf_100" "merge_sort_100" "matrix_mul_100" "fibonacci_1000" "fibonacci_iterative_pretty_1000" "lanczos_1000" "spf_1000" "merge_sort_1000" "matrix_mul_1000" )
# Base directories
base_dir="~/occpNaive"
polygon_dir="Docker/polygonNetwork"
localstack_dir="Docker/localstack"
hardhat_dir="$polygon_dir/hardhat"
data_results_dir="data/results"

# Call the restart script in Docker/polygon
if [ -x "$polygon_dir/restart.sh" ]; then
	echo "Executing restart script in $polygon_dir..."
	(cd "$polygon_dir" && ./restart.sh)
else
	echo "Restart script not found or not executable in $polygon_dir"
fi

# Go into Docker/polygon/hardhat and execute build.sh
if [ -x "$hardhat_dir/build_and_deploy_naive.sh" ]; then
	rm "$hardhat_dir/contracts_naive.dat"
	echo "Executing build.sh in $hardhat_dir..."
	(cd "$hardhat_dir" && ./build_and_deploy_naive.sh)
else
	echo "build_and_deploy_naive.sh not found or not executable in $hardhat_dir"
fi
# Call the restart script in Docker/localstack
if [ -x "$localstack_dir/restart.sh" ]; then
	echo "Executing restart script in $localstack_dir..."
	(cd "$localstack_dir" && ./restart.sh)
else
	echo "Restart script not found or not executable in $localstack_dir"
fi
# Loop through each tuple
for program in "${tuples[@]}"; do
	echo "Processing naive run Program=$program..."

	# Start the Python script with argument X and wait for it to finish
	python_script="runner.py"  # Replace with the actual Python script name
	if [ -f "$python_script" ]; then
		echo "Running Python script: $python_script with arguments program=$program"
		python "$python_script" --runtype 2 --program "$program" --step_size 100000000000 >> data/naive_output.dat
	else
		echo "Python script not found: $python_script"
		exit 1
	fi
	
	echo "Processing for naive Program=$program completed."
	echo "-----------------------------------"
done

echo "All tasks completed."
