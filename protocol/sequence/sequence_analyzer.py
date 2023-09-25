import hashlib

import networkx as nx
import numpy as np


class SequenceAnalyzer:
    def run(self, sequence):
        majority_error_votes, conflicts, quorum_sequence = self.check_for_conflicts(sequence)
        if majority_error_votes:
            print("Majority of workers voted for ERROR!")
            return [], [hashlib.sha256("AllErrorVotes".encode()).digest()]
        if len(conflicts) > 0:
            print("Conflicts:")
            print(conflicts)
            return conflicts, []
        else:
            pos_sequence = self.reconstruct_sequence(quorum_sequence)
            print(f"Reconstructed a possible sequence:")
        return conflicts, pos_sequence

    @staticmethod
    def has_cycles(graph):
        return len(list(nx.simple_cycles(graph))) > 0, list(np.squeeze(list(nx.simple_cycles(graph))))

    @staticmethod
    def find_error_votes(sequence):
        error_hash = b'\xd9\x8e\xe0\xe5\xf99\x9d\xb98\x10\x14\xc9\xf8\x90\xf8\x96\xd3\xfc\xb2r\xc2\xa7\xa5!\xd0\xa1:\xa20\x85\xa2\x84'
        conflicts = set()
        for seq in sequence:
            if seq[1] == error_hash:
                conflicts.add(seq[0])
        return len(conflicts) > len(sequence) * 0.8, conflicts

    @staticmethod
    def check_outgoing_conflicts(sequence):
        # Step 1: Create a dictionary to store the votes for each outgoing edge
        vote_counts = {}

        # Step 2: Populate the vote counts in the dictionary
        for edge in sequence:
            source, target, _, _, _, _ = edge
            if source not in vote_counts:
                vote_counts[source] = {}
            if target not in vote_counts[source]:
                vote_counts[source][target] = 0
            vote_counts[source][target] += 1

        # Step 3: Check for conflicts
        conflicts = []
        for source, targets in vote_counts.items():
            for target, count in targets.items():
                if count > 1:
                    conflicts.append((source, target))
        if conflicts:
            print("Outgoing conflicts:")
            for conflict in conflicts:
                print(f"Node {conflict[0]} has multiple outgoing edges to Node {conflict[1]}")
        else:
            print("No outgoing conflicts found.")
        return conflicts

    @staticmethod
    def check_outgoing_quorum(task_sequences):
        output_map = {x[0]: {} for x in task_sequences}

        for sequence in task_sequences:
            # outgoing
            elem = output_map.get(sequence[0])
            if sequence[1] in elem:
                elem[sequence[1]] += 1
            else:
                elem.update({sequence[1]: 1})

        quorum_sequence = set()
        conflicts = set()
        for inp, targets in output_map.items():
            max_keys = [
                key for key, value in targets.items() if value == max(targets.values())
            ]

            if len(max_keys) > 1:
                conflicts.add(inp)
            else:
                quorum_output = max_keys[0]
                quorum_sequence.add((inp, quorum_output))

        return conflicts, quorum_sequence

    def get_conflicts(self, task_sequences):
        conflicts, out_seq = self.check_outgoing_quorum(task_sequences)
        if len(conflicts) > 0:
            return conflicts, []
        input_map = {x[1]: {} for x in out_seq}

        conflicts = set()
        for sequence in out_seq:
            if sequence[0] == sequence[1]:
                conflicts.add(sequence[0])
            # incoming
            elem = input_map.get(sequence[1])
            if sequence[0] in elem:
                elem[sequence[0]] += 1
            else:
                elem.update({sequence[0]: 1})

        quorum_two = set()
        quorum_sequence = set()
        for target, inputs in input_map.items():
            max_keys = [
                key for key, value in inputs.items() if value == max(inputs.values())
            ]

            if len(max_keys) > 1:
                [conflicts.add(x) for x in max_keys]
            else:
                quorum_input = max_keys[0]
                quorum_sequence.add((quorum_input, target))
                if max(inputs.values()) > 1:
                    quorum_two.add((quorum_input, target))

        return conflicts, quorum_sequence

    def check_for_conflicts(self, sequence):
        conflicts = set()
        # 1 - Check for all ERROR votes!
        majority_error_votes, error_sequences = self.find_error_votes(sequence)
        [conflicts.add(x) for x in error_sequences]
        if majority_error_votes:
            return majority_error_votes, conflicts, []
        new_conflicts, quorum_seq = self.get_conflicts(sequence)
        [conflicts.add(x) for x in new_conflicts]
        if len(conflicts) > 0:
            return False, conflicts, []
        majority_edges = quorum_seq
        graph = nx.DiGraph()
        graph.add_edges_from([(x[0], x[1]) for x in majority_edges])
        has_cyc, cycle = self.has_cycles(graph)
        [conflicts.add(x) for x in cycle]
        return majority_error_votes, conflicts, quorum_seq

    @staticmethod
    def find_conflicts(task_sequences):
        input_map = {x[1]: {} for x in task_sequences}
        conflicts = set()
        for sequence in task_sequences:
            if sequence[0] == sequence[1]:
                conflicts.add(sequence[0])
            elem = input_map.get(sequence[1])
            if sequence[0] in elem:
                elem[sequence[0]] += 1
            else:
                elem.update({sequence[0]: 1})

        quorum_two = []
        quorum_sequence = []
        for target, inputs in input_map.items():
            max_keys = [
                key for key, value in inputs.items() if value == max(inputs.values())
            ]

            if len(max_keys) > 1:
                [conflicts.add(x) for x in max_keys]
            else:
                quorum_input = max_keys[0]
                quorum_sequence.append((quorum_input, target))
                if max(inputs.values()) > 1:
                    quorum_two.append((quorum_input, target))

        return conflicts, quorum_sequence, quorum_two

    @staticmethod
    def find_first_trace(quorum_sequences):
        for inp, trg1 in quorum_sequences:
            found = False
            for _, trg in quorum_sequences:
                if inp == trg:
                    found = True
                    break
            if not found:
                return inp, trg1

    @staticmethod
    def find_next_trace(current, quorum_sequences):
        for src, trg in quorum_sequences:
            if current == src:
                return trg

    @staticmethod
    def has_cycle_and_no_gaps(edges):
        nodes = set()
        for edge in edges:
            nodes.add(edge[0])
            nodes.add(edge[1])

        visited = {node: False for node in nodes}
        stack = {node: False for node in nodes}

        def has_cycle(node):
            visited[node] = True
            stack[node] = True

            for edge in edges:
                if edge[0] == node:
                    neighbor = edge[1]
                    if not visited[neighbor]:
                        if has_cycle(neighbor):
                            return True
                    elif stack[neighbor]:
                        return True

            stack[node] = False
            return False

        for node in nodes:
            if not visited[node]:
                if has_cycle(node):
                    return True

        # Check for transition gaps
        for node in nodes:
            if not visited[node]:
                return True

        return False

    def reconstruct_sequence(self, quorum_sequences):
        reconstructed_sequence = []
        first_elem, second_elem = self.find_first_trace(quorum_sequences)
        if not first_elem:
            return "Reconstruction error"

        reconstructed_sequence.append(first_elem)
        reconstructed_sequence.append(second_elem)

        cur_elem = second_elem
        while True:
            next_elem = self.find_next_trace(cur_elem, quorum_sequences)
            if next_elem:
                reconstructed_sequence.append(next_elem)
                cur_elem = next_elem
            else:
                break

        if len(reconstructed_sequence) == len(quorum_sequences) + 1:
            return reconstructed_sequence
        else:
            return "Reconstruction error"
