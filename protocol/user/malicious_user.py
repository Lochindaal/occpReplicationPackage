import hashlib

from eth_abi.packed import encode_packed

from protocol.user.base_user import BaseUser
from utils.trace_utils import compute_trace_hash


class MaliciousUser(BaseUser):

    # Create a fake sequence hash
    def create_sequence_hash(self, sequence_list):
        sequence_hashes = []
        for i in range(len(sequence_list) - 1):
            sequence_hashes.append(compute_trace_hash(sequence_list[i]["trace"]))
        sequence_hashes.append(hashlib.sha256("5".encode()).digest())
        target_sequence = hashlib.sha256(
            encode_packed(["bytes32[]"], [sequence_hashes])
        ).digest()
        return target_sequence, sequence_hashes
