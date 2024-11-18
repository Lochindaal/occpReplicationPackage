#!/bin/bash

# Validate that an integer argument is provided
if [[ $# -eq 0 || ! "$1" =~ ^[0-9]+$ ]]; then
    echo "Usage: $0 <integer>"
    exit 1
fi

# Store the integer argument in a variable
runtype="$1"
program="$2"
step_size="$3"

# Call the Python script and pass the integer argument
nohup python -u runner.py --runtype "$runtype" --program "$program" --step_size "$step_size" > data/local_output.dat >&1 &
