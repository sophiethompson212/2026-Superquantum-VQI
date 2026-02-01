import numpy as np
import subprocess
import tempfile
import os
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import Operator
from qiskit.compiler import transpile
from qiskit.circuit.library import UnitaryGate
from scipy.linalg import cossin
U = np.array([
    [0.1448081895 + 0.1752383997j, -0.5189281551 - 0.5242425896j, 
     -0.1495585824 + 0.312754999j, 0.1691348143 - 0.5053863118j],
    [-0.9271743926 - 0.0878506193j, -0.1126033063 - 0.1818584963j, 
     0.1225587186 + 0.0964028611j, -0.2449850904 - 0.0504584131j],
    [-0.0079842758 - 0.2035507051j, -0.3893205530 - 0.0518092515j, 
     0.2605170566 + 0.3286402481j, 0.4451730754 + 0.6558933250j],
    [0.0313792249 + 0.1961395216j, 0.4980474972 + 0.0884604926j, 
     0.3407886532 + 0.7506609982j, 0.0146480652 - 0.1575584270j]
])


def matrix_to_su2(U_2x2):
    """Convert 2x2 unitary to SU(2) format"""
    det = np.linalg.det(U_2x2)
    global_phase = np.angle(det) / 2
    SU = U_2x2 / np.exp(1j * global_phase)
    return SU, global_phase


def su2_to_axis_angle(SU_matrix):
    """
    Convert SU(2) matrix to axis-angle representation for GridSynth
    SU(2) = exp(i * theta/2 * (n_x*X + n_y*Y + n_z*Z))
    """
    # Extract the rotation axis and angle
    # SU(2) = [[a, -b*], [b, a*]] where |a|^2 + |b|^2 = 1
    
    a = SU_matrix[0, 0]
    b = SU_matrix[1, 0]
    
    # Angle of rotation
    theta = 2 * np.arctan2(np.abs(b), np.abs(a))
    
    # If theta is very small, it's essentially identity
    if theta < 1e-10:
        return 0, 0, 0, 0
    
    # Rotation axis (Bloch sphere coordinates)
    # This is a simplified conversion - GridSynth expects specific format
    
    # For GridSynth, we need to express as rotation around axis
    # Let's use the trace formula: Tr(U) = 2*cos(theta/2)
    trace = np.trace(SU_matrix)
    theta = 2 * np.arccos(np.real(trace) / 2)
    
    if abs(theta) < 1e-10:
        return 0, 0, 0, 0
    
    # Extract axis from the anti-hermitian part
    U_minus_Udag = SU_matrix - SU_matrix.conj().T
    
    nx = np.imag(U_minus_Udag[0, 1])
    ny = np.real(U_minus_Udag[0, 1])  
    nz = np.imag(U_minus_Udag[0, 0])
    
    # Normalize
    norm = np.sqrt(nx**2 + ny**2 + nz**2)
    if norm > 1e-10:
        nx, ny, nz = nx/norm, ny/norm, nz/norm
    
    return theta, nx, ny, nz


def call_gridsynth(theta, nx, ny, nz, precision=1e-10):
    """
    Call gridsynth command line tool
    
    GridSynth typical usage:
    gridsynth -b 10 -p angle
    
    where angle is the rotation angle
    """
    
    print(f"   Calling GridSynth: theta={theta:.6f}, axis=({nx:.3f}, {ny:.3f}, {nz:.3f})")
    
    # GridSynth usually takes angle as input
    # Try different command formats:
    
    commands_to_try = [
        ['gridsynth', '-b', '10', '-p', str(theta)],
        ['gridsynth', str(theta)],
        ['gridsynth', '-p', str(theta)],
    ]
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                print(f"   GridSynth output: {output[:100]}...")
                return parse_gridsynth_output(output)
            
        except Exception as e:
            continue
    
    print(f"   ✗ GridSynth call failed")
    return None


def parse_gridsynth_output(output):
    """
    Parse GridSynth output to get gate sequence
    Output is usually like: "THSTHTSTHT" or similar
    """
    gates = []
    
    # GridSynth outputs a string of gates
    i = 0
    output = output.upper().strip()
    
    # Remove any non-gate characters
    gate_str = ''.join(c for c in output if c in 'HTSXYZW*')
    
    i = 0
    while i < len(gate_str):
        if i < len(gate_str) - 1 and gate_str[i:i+2] == 'T*':
            gates.append('tdg')
            i += 2
        elif i < len(gate_str) - 1 and gate_str[i:i+2] == 'S*':
            gates.append('sdg')
            i += 2
        elif gate_str[i] == 'H':
            gates.append('h')
            i += 1
        elif gate_str[i] == 'T':
            gates.append('t')
            i += 1
        elif gate_str[i] == 'S':
            gates.append('s')
            i += 1
        elif gate_str[i] in ['X', 'Y', 'Z']:
            gates.append(gate_str[i].lower())
            i += 1
        else:
            i += 1
    
    return gates


def decompose_single_qubit_with_gridsynth(U_2x2, label=""):
    """
    Decompose a single-qubit unitary using GridSynth CLI
    """
    print(f"\n   Decomposing {label}...")
    
    # Convert to SU(2)
    SU, global_phase = matrix_to_su2(U_2x2)
    
    # Convert to axis-angle
    theta, nx, ny, nz = su2_to_axis_angle(SU)
    
    # Call GridSynth
    gates = call_gridsynth(theta, nx, ny, nz)
    
    if gates is None:
        print(f"   ✗ GridSynth failed, using Qiskit fallback")
        # Fallback: use Qiskit
        qc_temp = QuantumCircuit(1)
        qc_temp.append(UnitaryGate(U_2x2), [0])
        qc_temp = qc_temp.decompose().decompose()
        
        transpiled = transpile(
            qc_temp,
            basis_gates=['h', 's', 'sdg', 't', 'tdg'],
            optimization_level=3
        )
        
        # Extract gates
        gates = []
        for instr in transpiled.data:
            gates.append(instr.operation.name)
    
    t_count = gates.count('t') + gates.count('tdg')
    print(f"   ✓ Got {len(gates)} gates ({t_count} T gates)")
    
    return gates


def compile_with_gridsynth_cli(U_matrix):
    """
    Compile 2-qubit unitary using CS decomposition + GridSynth CLI
    """
    print("="*80)
    print("COMPILATION WITH GRIDSYNTH CLI")
    print("="*80)
    
    # Step 1: Cosine-Sine Decomposition
    print("\n1. Cosine-Sine Decomposition...")
    (u1, u2), theta, (v1h, v2h) = cossin(U_matrix, p=2, q=2, separate=True)
    
    v1 = v1h.T.conj()
    v2 = v2h.T.conj()
    
    print(f"   Decomposed into 4 single-qubit unitaries + {len(theta)} rotations")
    
    # Step 2: Decompose each single-qubit unitary with GridSynth
    print("\n2. Decomposing single-qubit gates with GridSynth...")
    
    single_qubits = [
        ('V1', v1, 0),
        ('V2', v2, 1),
        ('U1', u1, 0),
        ('U2', u2, 1)
    ]
    
    gate_sequences = {}
    total_t = 0
    
    for name, U_2x2, qubit in single_qubits:
        gates = decompose_single_qubit_with_gridsynth(U_2x2, label=name)
        gate_sequences[name] = (gates, qubit)
        
        t_count = gates.count('t') + gates.count('tdg')
        total_t += t_count
    
    print(f"\n   Total T-gates from single-qubit: {total_t}")
    
    # Step 3: Handle controlled rotations
    print("\n3. Decomposing controlled rotations...")
    
    qc_rot = QuantumCircuit(2)
    for angle in theta:
        qc_rot.cry(2*angle, 0, 1)
    
    qc_rot_decomposed = qc_rot.decompose().decompose()
    
    rot_transpiled = transpile(
        qc_rot_decomposed,
        basis_gates=['cx', 'h', 's', 'sdg', 't', 'tdg'],
        optimization_level=3
    )
    
    rot_ops = rot_transpiled.count_ops()
    t_rot = rot_ops.get('t', 0) + rot_ops.get('tdg', 0)
    print(f"   Rotations: {t_rot} T gates, {rot_ops.get('cx', 0)} CNOTs")
    
    # Step 4: Build full circuit
    print("\n4. Building full circuit...")
    
    qc = QuantumCircuit(2)
    
    # Apply V gates
    for gate in gate_sequences['V1'][0]:
        getattr(qc, gate)(0)
    
    for gate in gate_sequences['V2'][0]:
        getattr(qc, gate)(1)
    
    # Add rotation circuit
    qc.compose(rot_transpiled, inplace=True)
    
    # Apply U gates
    for gate in gate_sequences['U1'][0]:
        getattr(qc, gate)(0)
    
    for gate in gate_sequences['U2'][0]:
        getattr(qc, gate)(1)
    
    # Final optimization
    print("\n5. Final optimization...")
    final = transpile(
        qc,
        basis_gates=['cx', 'h', 's', 'sdg', 't', 'tdg'],
        optimization_level=3
    )
    
    ops = final.count_ops()
    t_total = ops.get('t', 0) + ops.get('tdg', 0)
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"  T-count: {t_total}")
    print(f"  CNOTs: {ops.get('cx', 0)}")
    print(f"  Depth: {final.depth()}")
    print(f"  Total gates: {sum(ops.values())}")
    
    # Verify
    print("\n6. Verifying...")
    compiled_op = Operator(final)
    target_op = Operator(U_matrix)
    fidelity = np.abs(np.trace(compiled_op.data.conj().T @ target_op.data)) / 4
    print(f"   Fidelity: {fidelity:.10f}")
    
    return final


# Main execution
if __name__ == "__main__":
    print("="*80)
    print("TESTING GRIDSYNTH CLI")
    print("="*80)
    
    # First, test if gridsynth is available
    print("\nChecking GridSynth availability...")
    try:
        result = subprocess.run(['gridsynth', '--help'], capture_output=True, timeout=5)
        print("✓ GridSynth found!")
        print(f"Output: {result.stdout.decode()[:200]}")
    except:
        print("✗ GridSynth not found in PATH")
        print("Please ensure gridsynth is installed and in your PATH")
        exit(1)
    
    # Compile the unitary
    print("\n" + "="*80)
    print("COMPILING RANDOM UNITARY")
    print("="*80)
    
    circuit = compile_with_gridsynth_cli(U)
    
    if circuit:
        # Save result
        try:
            qasm_str = qasm2.dumps(circuit)
        except:
            qasm_str = str(circuit)
        
        with open('random_unitary_gridsynth.qasm', 'w') as f:
            f.write(qasm_str)
        
        print("\n✓ Saved to: random_unitary_gridsynth.qasm")
    else:
        print("\n✗ Compilation failed")