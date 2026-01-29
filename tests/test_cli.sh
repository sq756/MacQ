#!/bin/bash
# MacQ CLI Integration Test Suite
# Demonstrates: Load -> Simulate -> Optimize -> Analyze -> Export

set -e # Exit on error

echo "=== MacQ CLI Integration Test ==="

# 1. Create a test circuit
echo "Step 1: Creating a redundant QFT-like circuit..."
cat <<EOF > tests/demo.ql
qubits 3
H 0
H 0
X 1
CNOT 0-1
CNOT 1-2
Toffoli 0-1-2
EOF

# 2. Run simulation (Headless)
echo "Step 2: Running simulation (text output)..."
python3 macq_cli.py run tests/demo.ql -s 1000

# 3. Optimize circuit
echo "Step 3: Optimizing circuit (removing double H)..."
python3 macq_cli.py optimize tests/demo.ql > tests/demo_opt.ql
echo "Original gates: $(grep -c "[HXZ]" tests/demo.ql)"
echo "Optimized gates: $(grep -c "[HXZ]" tests/demo_opt.ql)"

# 4. Analyze circuit properties
echo "Step 4: Analyzing circuit (JSON output)..."
python3 macq_cli.py analyze tests/demo_opt.ql

# 5. Export results to CSV
echo "Step 5: Exporting measurement counts to CSV..."
python3 macq_cli.py run tests/demo_opt.ql -s 5000 -f csv > tests/results.csv
head -n 5 tests/results.csv

echo -e "\n✅ CLI Integration Test Passed!"
rm tests/demo.ql tests/demo_opt.ql tests/results.csv
