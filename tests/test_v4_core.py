import numpy as np
from macq.core.oracle import OracleBuilder
from macq.core.challenge import calculate_fidelity, ChallengeJudge
import os

def test_oracle():
    print("Testing Oracle Builder...")
    # (q0 & q1)
    gates = OracleBuilder.build_from_expression("(q0 & q1)", ["q0", "q1"], "q2")
    print(f"Generated {len(gates)} gates for (q0 & q1)")
    # Should have at least one MCX if q0=1, q1=1
    assert any(g['type'] == 'MCX' for g in gates)
    print("Oracle Builder core logic: PASS")

def test_challenge():
    print("Testing Challenge Logic...")
    v1 = np.array([1, 0, 0, 0])
    v2 = np.array([1, 0, 0, 0])
    f = calculate_fidelity(v1, v2)
    assert f > 0.99
    
    v3 = np.array([0, 1, 0, 0])
    f2 = calculate_fidelity(v1, v3)
    assert f2 < 0.01
    print("Fidelity calculation: PASS")

if __name__ == "__main__":
    try:
        test_oracle()
        test_challenge()
        print("\nAll Core v4.0 Logic Verified.")
    except Exception as e:
        print(f"\nVerification FAILED: {e}")
        exit(1)
