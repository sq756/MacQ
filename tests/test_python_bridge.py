#!/usr/bin/env python3
"""
MacQ Python Bridge Test Suite
"""

import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from macq import QuantumState, version

def test_version():
    """Test library version"""
    v = version()
    print(f"✓ Version: {v}")
    assert "MacQ" in v

def test_create_state():
    """Test state creation"""
    qs = QuantumState(3)
    assert qs.num_qubits == 3
    assert qs.vector_size == 8
    print(f"✓ Created 3-qubit state: {qs}")

def test_single_qubit_gates():
    """Test single-qubit gates"""
    qs = QuantumState(1)
    
    # X gate
    qs.x(0)
    prob = qs.probability(0)
    assert abs(prob - 1.0) < 1e-6
    print(f"✓ X gate: |1⟩ probability = {prob:.6f}")
    
    # H gate
    qs = QuantumState(1)
    qs.h(0)
    prob = qs.probability(0)
    assert abs(prob - 0.5) < 1e-6
    print(f"✓ H gate: |1⟩ probability = {prob:.6f} (expected 0.5)")

def test_bell_state():
    """Test Bell state creation"""
    qs = QuantumState(2)
    qs.h(0).cnot(0, 1)
    
    probs = qs.probabilities()
    assert abs(probs[0] - 0.5) < 1e-6  # |00⟩
    assert abs(probs[3] - 0.5) < 1e-6  # |11⟩
    assert abs(probs[1]) < 1e-6  # |01⟩
    assert abs(probs[2]) < 1e-6  # |10⟩
    
    print(f"✓ Bell state: P(|00⟩)={probs[0]:.3f}, P(|11⟩)={probs[3]:.3f}")

def test_statevector():
    """Test statevector extraction"""
    qs = QuantumState(2)
    qs.h(0).h(1)
    
    vec = qs.get_statevector()
    assert vec.shape == (4,)
    assert np.allclose(np.abs(vec), 0.5)
    print(f"✓ Statevector: {vec}")

def test_measurement():
    """Test measurement"""
    qs = QuantumState(1)
    qs.h(0)
    
    # Measure many times
    results = [qs.clone().measure(0) for _ in range(100)]
    ones = sum(results)
    ratio = ones / 100
    
    assert 0.3 < ratio < 0.7  # Should be ~50%
    print(f"✓ Measurement: {ones}/100 ones ({ratio:.1%})")

def test_multi_qubit():
    """Test larger state"""
    qs = QuantumState(10)
    for i in range(10):
        qs.h(i)
    
    probs = qs.probabilities()
    assert np.allclose(probs, 1.0/1024)
    print(f"✓ 10-qubit uniform superposition: all probs ≈ {1/1024:.6f}")

if __name__ == '__main__':
    print("=" * 50)
    print("MacQ Python Bridge Test Suite")
    print("=" * 50)
    
    tests = [
        test_version,
        test_create_state,
        test_single_qubit_gates,
        test_bell_state,
        test_statevector,
        test_measurement,
        test_multi_qubit
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            sys.exit(1)
    
    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
