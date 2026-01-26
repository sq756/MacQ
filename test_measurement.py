#!/usr/bin/env python3
"""
Test measurement syntax in Q-Lang v2.0
"""

import sys
sys.path.insert(0, '/Volumes/External/Reaearch/quantum_eng')

from macq.qlang import QLangParser

parser = QLangParser()

# Test 1: Simple measurement
print("Test 1: Simple measurement")
print("=" * 60)
code1 = """
H 0
measure 0 -> C0
"""
try:
    ast1 = parser.parse(code1)
    print(ast1)
    print("✅ Parsed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 2: Bell state with measurement
print("Test 2: Bell state with measurements")
print("=" * 60)
code2 = """
H 0
CNOT 0-1
measure 0 -> C0
measure 1 -> C1
"""
try:
    ast2 = parser.parse(code2)
    print(ast2)
    print("✅ Parsed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 3: Parallel gates and measurement
print("Test 3: Mixed operations")
print("=" * 60)
code3 = """
H 0, 1
CNOT 0-1; measure 2 -> C2
measure 0 -> C0; measure 1 -> C1
"""
try:
    ast3 = parser.parse(code3)
    print(ast3)
    print("✅ Parsed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎉 All measurement parsing tests completed!")
