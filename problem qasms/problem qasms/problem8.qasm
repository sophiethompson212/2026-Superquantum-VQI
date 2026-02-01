OPENQASM 2.0; 
include "qelib1.inc";
qreg q[2]; h q[1]; t q[1]; cx q[0], q[1]; tdg q[1]; cx q[0], q[1]; t q[0]; h q[0]; cx q[0], q[1]; cx q[1], q[0]; cx q[0], q[1];

https://www.researchgate.net/figure/Quantum-circuit-C2-for-the-two-qubit-quantum-Fourier-transformation_fig5_329771282
