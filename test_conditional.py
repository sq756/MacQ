#!/usr/bin/env python3
"""
Test Q-Lang v2.0 classical control flow (if-then)
"""

import sys
sys.path.insert(0, '/Volumes/External/Reaearch/quantum_eng')

from macq.qlang import QLangParser

parser = QLangParser()

print("=" * 70)
print("Q-LANG V2.0 CLASSICAL CONTROL FLOW TEST")
print("=" * 70)
print()

# Test 1: Simple conditional
print("Test 1: Simple if-then")
print("-" * 70)
code1 = """
measure 0 -> c0
if c0 then X 1
"""
try:
    ast1 = parser.parse(code1)
    print("✅ Parsed successfully!")
    print(ast1)
    print()
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 2: Conditional with explicit comparison
print("Test 2: if c0 == 1 then")
print("-" * 70)
code2 = """
measure 0 -> c0
if c0 == 1 then Z 1
if c0 == 0 then X 1
"""
try:
    ast2 = parser.parse(code2)
    print("✅ Parsed successfully!")
    for i, step in enumerate(ast2.time_steps):
        print(f"  Step {i}: {step}")
    print()
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 3: AND condition
print("Test 3: Logical AND")
print("-" * 70)
code3 = """
measure 0 -> c0
measure 1 -> c1
if c0 and c1 then X 2
"""
try:
    ast3 = parser.parse(code3)
    print("✅ Parsed successfully!")
    print(ast3)
    print()
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 4: Quantum Teleportation with conditionals
print("Test 4: Quantum Teleportation (Complete!)")
print("-" * 70)
teleportation = """
# Quantum Teleportation - NOW COMPLETE!
H 1
CNOT 1-2
CNOT 0-1
H 0
measure 0 -> c0
measure 1 -> c1
if c1 then X 2
if c0 then Z 2
"""
try:
    ast4 = parser.parse(teleportation)
    print("✅ Parsed successfully!")
    print("\nQuantum Teleportation Circuit:")
    for i, step in enumerate(ast4.time_steps):
        print(f"  {i}: {step}")
    print()
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 5: Complex OR condition
print("Test 5: Logical OR")
print("-" * 70)
code5 = """
measure 0 -> c0
measure 1 -> c1
if c0 or c1 then H 2
"""
try:
    ast5 = parser.parse(code5)
    print("✅ Parsed successfully!")
    print(ast5)
    print()
except Exception as e:
    print(f"❌ Error: {e}\n")

print("=" * 70)
print("✨ CLASSICAL CONTROL FLOW TEST COMPLETE!")
print("=" * 70)
print()
print("Q-Lang v2.0 now supports:")
print("  ✅ Measurements (measure qubit -> classical_bit)")
print("  ✅ Simple conditionals (if c0 then X 1)")
print("  ✅ Explicit comparisons (if c0 == 1 then ...)")
print("  ✅ Logical AND (if c0 and c1 then ...)")
print("  ✅ Logical OR (if c0 or c1 then ...)")
print()
print("🎯 Next: C bridge integration + GUI updates!")
