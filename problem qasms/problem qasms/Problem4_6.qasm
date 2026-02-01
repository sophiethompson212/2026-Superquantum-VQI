OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];

// Fidelity of -d = 6

// --- Part 1: exp(i*pi/7 * XX) ---
h q[0];
h q[1];
cx q[0], q[1];

// Optimal Rz(-2pi/7) approximation starts here
t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1];
s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1];
h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1];
s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1];
t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1];
t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1];
// End Rz approximation

cx q[0], q[1];
h q[0];
h q[1];

// --- Part 2: exp(i*pi/7 * YY) ---
sdg q[0];
sdg q[1];
h q[0];
h q[1];
cx q[0], q[1];

// Optimal Rz(-2pi/7) approximation starts here
t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1];
s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1];
h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1];
t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1];
s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1]; s q[1]; t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1];
t q[1]; h q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1];
t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1]; h q[1]; s q[1]; t q[1];
h q[1];
// End Rz approximation

cx q[0], q[1];
h q[0];
h q[1];
s q[0];
s q[1];

