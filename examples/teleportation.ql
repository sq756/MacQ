# ============================================================
# QUANTUM TELEPORTATION
# Transferring state from Q0 to Q2 via Q1 (Entangled pair)
# ============================================================
qubits 3

# Step 1: Prepare state to teleport on Q0 (e.g., |1>)
X 0

# Step 2: Prepare Bell pair on Q1 and Q2
H 1
CNOT 1-2

# Step 3: Alice performs Bell measurement on Q0 and Q1
CNOT 0-1
H 0
measure 0 -> c0
measure 1 -> c1

# Step 4: Bob applies corrections based on Alice's results
if c1 then X 2
if c0 then Z 2
