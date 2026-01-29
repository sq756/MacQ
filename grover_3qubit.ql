# ============================================================
# GROVER'S ALGORITHM: 3-Qubit Search
# Searching for the state |111>
# ============================================================
qubits 3

# Step 1: Superposition
H 0, 1, 2

# Step 2: Oracle (Marks |111>)
# For |111>, we use a multi-controlled Z (Toffoli with H on target)
H 2
Toffoli 0-1-2
H 2

# Step 3: Diffusion Operator (Amplification)
H 0, 1, 2
X 0, 1, 2
H 2
Toffoli 0-1-2
H 2
X 0, 1, 2
H 0, 1, 2

# Step 4: Measure
measure 0 -> c0
measure 1 -> c1
measure 2 -> c2
