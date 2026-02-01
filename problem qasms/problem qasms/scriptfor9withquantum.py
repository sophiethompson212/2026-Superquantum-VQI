# Required: qiskit
# pip install qiskit

import numpy as np
from qiskit import QuantumCircuit, transpile
from itertools import product


base_circuit_list = [
    ('h', 1),
    ('t', 1),
    ('cx', 0, 1),
    ('tdg', 1),
    ('cx', 0, 1),
    ('t', 0),
    ('h', 0),
    ('cx', 0, 1),
    ('cx', 1, 0),
    ('cx', 0, 1)
]


single_qubits = ['h', 't', 'tdg', 's', 'sdg']
cx_options = [None, ('cx', 0, 1), ('cx', 1, 0)]
all_gates = single_qubits + cx_options


max_extra_gates = 1000

def build_qiskit_circuit(gate_list):
    qc = QuantumCircuit(2)
    for g in gate_list:
        if g[0] == 'cx':
            qc.cx(g[1], g[2])
        else:
            getattr(qc, g[0])(g[1])
    return qc

def compute_unitary(gate_list):
    qc = build_qiskit_circuit(gate_list)
    return qc.unitary().data

def list_to_qasm(gate_list):
    lines = ["OPENQASM 2.0;", 'include "qelib1.inc";', 'qreg q[2];']
    for g in gate_list:
        if g[0] == 'cx':
            lines.append(f"cx q[{g[1]}], q[{g[2]}];")
        else:
            lines.append(f"{g[0]} q[{g[1]}];")
    return "\n".join(lines)

found = False
insertion_points = len(base_circuit_list) + 1


for n_extra in range(1, max_extra_gates + 1):
    for positions in product(range(insertion_points), repeat=n_extra):
        for gates in product(all_gates, repeat=n_extra):
            candidate = base_circuit_list.copy()
            # Insert extra gates in reverse order to not shift positions
            for pos, g in sorted(zip(positions, gates), reverse=True):
                if g is not None:
                    if isinstance(g, str):
                        # single-qubit gate: default qubit 0 for simplicity
                        candidate.insert(pos, (g, 0))
                    else:
                        # cx gate
                        candidate.insert(pos, g)
            # Compute unitary
            U_candidate = compute_unitary(candidate)
            if np.allclose(U_candidate, U_target, atol=1e-2):
                print("Found matching circuit!")
                print(list_to_qasm(candidate))
                found = True
                break
        if found:
            break
    if found:
        break

if not found:
    print("No matching circuit found with given extra gates and search depth.")
