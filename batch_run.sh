#!/bin/bash

# Define the array of X values
tuples=( "lanczos,3807" "spf,4981" "merge_sort,4993" "matrix_mul,4340" "fibonacci_10,34878" "fibonacci_iterative_pretty_10,49966"  "lanczos_10,38062" "spf_10,49809" "merge_sort_10,49861" "matrix_mul_10,43328" "fibonacci_100,348776" "fibonacci_iterative_pretty_100,499651" "lanczos_100,380611" "spf_100,498081" "merge_sort_100,498543" "matrix_mul_100,433212" "fibonacci_1000,3487751" "fibonacci_iterative_pretty_1000,4996501" "lanczos_1000,3806101" "spf_1000,4980801" "merge_sort_1000,4985358" "matrix_mul_1000,4332057" )

# Base directories
base_dir="~/occpRepl"
polygon_dir="Docker/polygonNetwork"
localstack_dir="Docker/localstack"
hardhat_dir="$polygon_dir/hardhat"
data_results_dir="data/results"

# Loop through each value of X
# Loop through each tuple
for pair in "${tuples[@]}"; do
	# Split the tuple into X and Y
	IFS=',' read -r x y <<< "$pair"
	echo "Processing X=$x and Y=$y..."

	# Call the restart script in Docker/polygon
	if [ -x "$polygon_dir/restart.sh" ]; then
		echo "Executing restart script in $polygon_dir..."
		(cd "$polygon_dir" && ./restart.sh)
	else
		echo "Restart script not found or not executable in $polygon_dir"
	fi
	
	# Go into Docker/polygon/hardhat and execute build.sh
	if [ -x "$hardhat_dir/build_and_deploy.sh" ]; then
		rm "$hardhat_dir/contracts.dat"
		echo "Executing build.sh in $hardhat_dir..."
		(cd "$hardhat_dir" && ./build_and_deploy.sh)
	else
		echo "build_and_deploy.sh not found or not executable in $hardhat_dir"
	fi
	
	# Call the restart script in Docker/localstack
	if [ -x "$localstack_dir/restart.sh" ]; then
		echo "Executing restart script in $localstack_dir..."
		(cd "$localstack_dir" && ./restart.sh)
	else
		echo "Restart script not found or not executable in $localstack_dir"
	fi
	
	# Start the Python script with argument X and wait for it to finish
	python_script="runner.py"  # Replace with the actual Python script name
	if [ -f "$python_script" ]; then
		echo "Running Python script: $python_script with arguments X=$x and Y=$y"
		python "$python_script" --runtype 1 --program "$x" --step_size "$y" >> data/local_output.dat
	else
		echo "Python script not found: $python_script"
		exit 1
	fi
	
	# Copy the folders data/results into a new folder based on the loop variable
	#cp -R data/results data/batch_results/
	#cp -R data/logs data/batch_results/
	#cp data/local_outputs.dat data/batch_results/
	echo "Processing for X=$x completed."
	echo "-----------------------------------"
done

echo "All tasks completed."
