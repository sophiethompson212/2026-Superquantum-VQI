import numpy as np
from itertools import combinations, product

# Target f(x) values from the problem
# f(x) = 4φ(x)/π where φ(x) is given in the problem
f_target = [
    0,  # 0000
    4,  # 0001
    5,  # 0010
    7,  # 0011
    5,  # 0100
    7,  # 0101
    6,  # 0110
    6,  # 0111
    5,  # 1000
    7,  # 1001
    6,  # 1010
    6,  # 1011
    6,  # 1100
    6,  # 1101
    7,  # 1110
    5   # 1111
]

print("=" * 70)
print("OPTIMAL PHASE POLYNOMIAL FINDER FOR 4-QUBIT DIAGONAL UNITARY")
print("=" * 70)
print(f"Target f(x) = 4φ(x)/π mod 8: {f_target}")
print()

# Generate all 15 non-zero linear functions L(x) = a·x mod 2
# a is 4-bit mask: a=1 (0001) to a=15 (1111)
# x is integer 0-15 representing 4-bit state
linear_funcs = []
linear_funcs_str = []  # Human-readable strings

for a in range(1, 16):  # a from 1 to 15
    L = []
    for x in range(16):
        # Compute dot product a·x mod 2
        dot = bin(a & x).count('1') % 2
        L.append(dot)
    linear_funcs.append(L)
    
    # Create string representation
    bits = []
    for i in range(4):
        if (a >> i) & 1:
            bits.append(f"x{i+1}")  # x1, x2, x3, x4
    if bits:
        func_str = " ⊕ ".join(bits)
    else:
        func_str = "0"
    linear_funcs_str.append(func_str)

print("All linear functions (a in binary = which qubits are XORed):")
for idx, func_str in enumerate(linear_funcs_str):
    a = idx + 1
    print(f"  L{idx:2d}: a={a:04b} = {func_str}")
print()

# Search for minimal T-count representation
best_solution = None
best_t_count = float('inf')
best_k = float('inf')

print("Searching for optimal phase polynomial representation...")
print("f(x) = Σ c_i·L_i(x) mod 8, minimize # of odd c_i (T-count)")
print()

# Try increasing number of terms
for k in range(1, 7):  # Try 1 to 6 terms
    print(f"Searching with k={k} terms...")
    
    for combo in combinations(range(15), k):
        # Try all coefficient combinations 0-7
        for c_vals in product(range(8), repeat=k):
            # Skip if all coefficients are 0
            if all(c == 0 for c in c_vals):
                continue
                
            # Check if this combination matches f_target for all x
            valid = True
            for x in range(16):
                total = 0
                for idx, c in zip(combo, c_vals):
                    total += c * linear_funcs[idx][x]
                if total % 8 != f_target[x]:
                    valid = False
                    break
            
            if valid:
                # Count T-gates = number of odd coefficients
                t_count = sum(1 for c in c_vals if c % 2 == 1)
                
                # Check if this is better than current best
                if t_count < best_t_count or (t_count == best_t_count and k < best_k):
                    best_t_count = t_count
                    best_k = k
                    best_solution = (k, combo, c_vals, t_count)
                    
                    print(f"  Found: T-count={t_count}, k={k}")
                    
                    # For very good solutions, show details
                    if t_count <= 5:
                        print(f"    Terms: {combo}")
                        print(f"    Coeffs: {c_vals}")

print()
print("=" * 70)

if best_solution:
    k, combo, c_vals, t_count = best_solution
    
    print(f"🎯 OPTIMAL SOLUTION FOUND!")
    print(f"   Number of terms (k): {k}")
    print(f"   T-count (odd coefficients): {t_count}")
    print()
    
    # Decode the solution
    print("Phase polynomial representation:")
    print("f(x) = ", end="")
    terms = []
    for idx, c in zip(combo, c_vals):
        if c != 0:
            term_str = f"{c}·({linear_funcs_str[idx]})"
            terms.append(term_str)
    print(" + ".join(terms) + "  (mod 8)")
    print()
    
    # Show what each coefficient means
    print("Term breakdown:")
    for idx, c in zip(combo, c_vals):
        if c != 0:
            phase = c * np.pi / 4
            gate = "Clifford" if c % 2 == 0 else f"T-count 1 (phase {phase:.3f}π)"
            print(f"  {c}·({linear_funcs_str[idx]}) → {gate}")
    print()
    
    # Verify thoroughly
    print("Full verification:")
    all_match = True
    for x in range(16):
        total = 0
        for idx, c in zip(combo, c_vals):
            total += c * linear_funcs[idx][x]
        computed = total % 8
        expected = f_target[x]
        
        # Convert x to binary string
        x_bin = format(x, '04b')  # MSB first: x1 x2 x3 x4
        
        match = (computed == expected)
        if not match:
            all_match = False
            
        print(f"  |{x_bin}⟩: computed={computed}, expected={expected} {'✓' if match else '✗'}")
    
    print()
    if all_match:
        print("✅ ALL STATES MATCH!")
    else:
        print("❌ SOME MISMATCHES!")
    
    # Circuit construction hints
    print()
    print("=" * 70)
    print("CIRCUIT CONSTRUCTION:")
    print("=" * 70)
    print("For each term c·L(x):")
    print("  1. Use CNOTs to compute L(x) into an ancilla qubit")
    print("  2. Apply Rz(cπ/4) on the ancilla:")
    for c in sorted(set(c_vals)):
        if c != 0:
            phase = c * np.pi / 4
            if c == 1:
                gate = "t     (T gate)"
            elif c == 3:
                gate = "t t t (T³ = S·T)"
            elif c == 5:
                gate = "tdg tdg tdg (T†³)"
            elif c == 7:
                gate = "tdg    (T† gate)"
            elif c % 2 == 0:
                gate = f"Clifford (e.g., S={c} for c=2)"
            else:
                gate = f"Rz({phase:.3f}π)"
            print(f"     c={c}: {gate}")
    print("  3. Uncompute L(x) (reverse CNOTs)")
    print()
    print(f"Total resources: T-count={t_count}, CNOTs≈{3*k} (with ancilla)")
    
else:
    print("❌ NO SOLUTION FOUND up to k=6 terms.")
    print("   Check if f_target array is correct.")

print("=" * 70)