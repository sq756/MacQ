#!/usr/bin/env python3
"""
Test script for Q-Lang validator
"""

import sys
sys.path.insert(0, '/Volumes/External/Reaearch/quantum_eng')

from macq.qlang import QLangParser
from macq.qlang.validator import QLangValidator, ValidationError

parser = QLangParser()

# Test 1: Valid Bell state
print("Test 1: Valid Bell state")
print("=" * 60)
code1 = """
H 0
CNOT 0-1
"""
ast1 = parser.parse(code1)
validator1 = QLangValidator(num_qubits=2)
try:
    validator1.validate(ast1)
    print("✅ Validation passed!")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
print()

# Test 2: Error - Qubit out of range
print("Test 2: Error - Qubit out of range")
print("=" * 60)
code2 = "H 5"
ast2 = parser.parse(code2)
validator2 = QLangValidator(num_qubits=3)
try:
    validator2.validate(ast2)
    print("✅ Validation passed!")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
print()

# Test 3: Error - Same qubit used twice in time step
print("Test 3: Error - Same qubit used twice")
print("=" * 60)
code3 = "H 0; X 0"
ast3 = parser.parse(code3)
validator3 = QLangValidator(num_qubits=3)
try:
    validator3.validate(ast3)
    print("✅ Validation passed!")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
print()

# Test 4: Error - Control = Target
print("Test 4: Error - Control = Target")
print("=" * 60)
code4 = "CNOT 0-0"
ast4 = parser.parse(code4)
validator4 = QLangValidator(num_qubits=3)
try:
    validator4.validate(ast4)
    print("✅ Validation passed!")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
print()

# Test 5: Valid parallel operations
print("Test 5: Valid parallel operations")
print("=" * 60)
code5 = "H 0, 2; X 1; CNOT 3-4"
ast5 = parser.parse(code5)
validator5 = QLangValidator(num_qubits=5)
try:
    validator5.validate(ast5)
    print("✅ Validation passed!")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
print()

# Test 6: Complex valid circuit
print("Test 6: Complex valid circuit")
print("=" * 60)
code6 = """
H 0, 2, 4; X 1, 3
CNOT 0-1; CNOT 2-3
Toffoli 0-1-2
"""
ast6 = parser.parse(code6)
validator6 = QLangValidator(num_qubits=5)
try:
    validator6.validate(ast6)
    print("✅ Validation passed!")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")

print("\n✅ All validator tests completed!")
