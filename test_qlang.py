#!/usr/bin/env python3
"""
Test script for Q-Lang parser
"""

import sys
sys.path.insert(0, '/Volumes/External/Reaearch/quantum_eng')

from macq.qlang import QLangParser

parser = QLangParser()

# Test 1: Bell state
print("Test 1: Bell state")
print("=" * 60)
code1 = """
H 0
CNOT 0-1
"""
ast1 = parser.parse(code1)
print(ast1)
print()

# Test 2: Parallel operations
print("Test 2: Parallel operations")
print("=" * 60)
code2 = "H 0, 2; X 1; CNOT 0-1"
ast2 = parser.parse(code2)
print(ast2)
print()

# Test 3: GHZ state
print("Test 3: GHZ state")
print("=" * 60)
code3 = """
H 0
CNOT 0-1
CNOT 0-2
"""
ast3 = parser.parse(code3)
print(ast3)
print()

# Test 4: Parametric gates
print("Test 4: Parametric rotation gates")
print("=" * 60)
code4 = """
Rx(3.14159/2) 0
Ry(π/4) 1
Rz(0.785) 2
"""
ast4 = parser.parse(code4)
print(ast4)
print()

# Test 5: Complex circuit
print("Test 5: Complex circuit")
print("=" * 60)
code5 = """
# Initialize
H 0, 2, 4; X 1, 3

# Entangle
CNOT 0-1; CNOT 2-3

# Toffoli
Toffoli 0-1-2
"""
ast5 = parser.parse(code5)
print(ast5)

print("\n✅ All tests passed!")
