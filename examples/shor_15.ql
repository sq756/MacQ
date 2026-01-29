# ============================================================
# SHOR'S ALGORITHM: Factorization of N=15
# Using a=7, period-finding to factor 15 = 3 × 5
# ============================================================
qubits 8

# Step 1: Initialize input register in equal superposition
H 0, 1, 2, 3

# Step 2: Initialize target register to |1>
X 4

# Step 3: Modular exponentiation: |x>|1> -> |x>|7^x mod 15>
MOD_EXP(7, 15) 0,1,2,3 -> 4,5,6,7

# Step 4: Inverse Quantum Fourier Transform on input register
QFT_INV 0, 1, 2, 3

# Step 5: Measure input register to find period
measure 0 -> c0
measure 1 -> c1
measure 2 -> c2
measure 3 -> c3
