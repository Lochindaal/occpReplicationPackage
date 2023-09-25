import json
import threading

# Create a lock to synchronize access to the file
file_lock = threading.Lock()

# Function that each thread will execute
def write_thread_safe(data, path):
    with file_lock:
        with open(path, "a") as file:
            json.dump(data, file)
            file.write('\n')  # Add a newline to separate JSON objects