#!/usr/bin/env python3
"""
Test script for Q-Lang compiler and decompiler
"""

import sys
sys.path.insert(0, '/Volumes/External/Reaearch/quantum_eng')

from macq.qlang import QLangParser
from macq.qlang.validator import QLangValidator
from macq.qlang.compiler import QLangCompiler, QLangDecompiler

parser = QLangParser()
compiler = QLangCompiler()
decompiler = QLangDecompiler()

# Test 1: Bell state
print("Test 1: Bell state compilation")
print("=" * 60)
code1 = """
H 0
CNOT 0-1
"""
ast1 = parser.parse(code1)
validator1 = QLangValidator(num_qubits=2)
validator1.validate(ast1)

gates1 = compiler.compile(ast1)
print("Compiled gates:")
for gate in gates1:
    print(f"  {gate}")

print("\nDecompiled code:")
decompiled1 = decompiler.decompile(gates1)
print(decompiled1)
print()

# Test 2: Complex circuit
print("Test 2: Complex circuit with parallel operations")
print("=" * 60)
code2 = """
H 0, 2, 4; X 1, 3
CNOT 0-1; CNOT 2-3
Toffoli 0-1-2
"""
ast2 = parser.parse(code2)
validator2 = QLangValidator(num_qubits=5)
validator2.validate(ast2)

gates2 = compiler.compile(ast2)
print("Compiled gates:")
for gate in gates2:
    print(f"  {gate}")

print("\nDecompiled code:")
decompiled2 = decompiler.decompile(gates2)
print(decompiled2)
print()

# Test 3: Parametric gates
print("Test 3: Parametric rotation gates")
print("=" * 60)
code3 = """
Rx(3.14159/2) 0
Ry(π/4) 1
Rz(1.5708) 2
"""
ast3 = parser.parse(code3)
validator3 = QLangValidator(num_qubits=3)
validator3.validate(ast3)

gates3 = compiler.compile(ast3)
print("Compiled gates:")
for gate in gates3:
    print(f"  {gate}")

print("\nDecompiled code:")
decompiled3 = decompiler.decompile(gates3)
print(decompiled3)

print("\n✅ All compiler tests completed!")
