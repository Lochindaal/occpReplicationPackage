import hashlib
import os.path
import pickle


def construct_file_path(base_path, idx, is_replay=False):
    file_name = f"{idx}_out_snap.pickle" if is_replay else f"{idx}_snap.pickle"
    return os.path.join(base_path, file_name)


def compute_trace_hash(trace):
    trace_dict = trace.__dict__
    # remove the exec mode
    del trace_dict["_exec_mode"]
    return hashlib.sha256((pickle.dumps(trace_dict))).digest()


def compare_traces_for_index(idx, base_path, storage, logger):
    input_hash = compute_trace_hash(storage.load(construct_file_path(base_path, idx)))
    expected_hash = compute_trace_hash(
        storage.load(construct_file_path(base_path, idx + 1))
    )
    result_hash = compute_trace_hash(
        storage.load(construct_file_path(base_path, idx, is_replay=True))
    )
    logger.info(
        f"Comparing result for Trace_{idx} "
        f"(h(input): {input_hash}): "
        f"{expected_hash} == {result_hash}"
        f" = {expected_hash == result_hash}"
    )
