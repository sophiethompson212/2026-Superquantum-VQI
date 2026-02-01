import numpy as np
import itertools
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator


target = np.array([
    [1, 0, 0, 0],
    [0, 0, (-1+1j)/2, (1+1j)/2],
    [0, 1j, 0, 0],
    [0, 0, (-1+1j)/2, (-1-1j)/2]
], dtype=complex)


tol = 0.01


single_qubit_gates = ['h','s','sdg','t','tdg']
two_qubit_gates = ['cx_01','cx_10']  # cx_01: q0->q1, cx_10: q1->q0


max_depth = 3  
max_cx = 1000     e

def apply_gate(qc, gate, qubits):
    if gate == 'h':
        qc.h(qubits)
    elif gate == 's':
        qc.s(qubits)
    elif gate == 'sdg':
        qc.sdg(qubits)
    elif gate == 't':
        qc.t(qubits)
    elif gate == 'tdg':
        qc.tdg(qubits)
    elif gate == 'cx_01':
        qc.cx(0,1)
    elif gate == 'cx_10':
        qc.cx(1,0)


single_sequences = list(itertools.product(single_qubit_gates, repeat=max_depth))
total_tests = 0
matches = []


for seq_q0 in single_sequences:
    for seq_q1 in single_sequences:
        
        for num_cx in range(max_cx+1):
            if num_cx == 0:
                cx_patterns = [[]]
            elif num_cx == 1:
                cx_patterns = [['cx_01'], ['cx_10']]
            else:
                cx_patterns = list(itertools.product(two_qubit_gates, repeat=2))

            for cx_seq in cx_patterns:
                # Build candidate circuit
                qc = QuantumCircuit(2)
                for g in seq_q0:
                    apply_gate(qc, g, 0)
                for g in seq_q1:
                    apply_gate(qc, g, 1)
                for g in cx_seq:
                    apply_gate(qc, g, None)
                
                # Evaluate unitary
                U = Operator(qc).data
                total_tests += 1

                # Check if it approximates target
                if np.allclose(U, target, atol=tol):
                    matches.append((seq_q0, seq_q1, cx_seq))

print(f"Total candidates tested: {total_tests}")
print(f"Matches found: {len(matches)}")
for m in matches:
    print("Q0 sequence:", m[0])
    print("Q1 sequence:", m[1])
    print("CX sequence:", m[2])
