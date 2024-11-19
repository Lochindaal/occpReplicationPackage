import math

multipliers = [1, 10, 100, 1000]
workers = 20

stepinfo = {
    "fibonacci": [69756, 697552, 6975502, 69755002],
    "fibonacci_iterative_pretty": [99934, 999304, 9993004, 99930004],
    "lanczos": [76128, 761226, 7612206, 76122006],
    "spf": [99619, 996163, 9961603, 99616003],
    "merge_sort": [99856, 997219, 9970849, 99707149],
    "matrix_mul": [86781, 866550, 8664240, 86641140],
}

for key in stepinfo.keys():
    print(key)
    print(list(map(lambda x: math.ceil(x / 20), stepinfo[key])))
