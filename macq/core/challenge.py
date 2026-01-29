"""
MacQ Challenge Mode Core Logic
Implements fidelity-based judging and challenge management.
"""

import json
import numpy as np
import os
from typing import List, Dict, Any, Optional
from macq.c_bridge import DensityMatrix

def calculate_fidelity(state1: np.ndarray, state2: np.ndarray) -> float:
    """
    Calculate the fidelity F = |<psi1|psi2>|^2 between two state vectors.
    If states are density matrices, this is a simplified pure-state fidelity check.
    """
    if state1.shape != state2.shape:
        return 0.0
    
    # |<state1|state2>|^2
    inner_product = np.vdot(state1, state2)
    fidelity = np.abs(inner_product)**2
    return float(fidelity)

class Challenge:
    def __init__(self, id: str, title: str, description: str, qubits: int, target_state: List[complex]):
        self.id = id
        self.title = title
        self.description = description
        self.qubits = qubits
        self.target_state = np.array(target_state, dtype=complex)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        # Convert JSON list of [real, imag] pairs back to complex numpy array
        target = [complex(x[0], x[1]) for x in data['target_state']]
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            qubits=data['qubits'],
            target_state=target
        )

class ChallengeJudge:
    def __init__(self, challenges_file: Optional[str] = None):
        if challenges_file is None:
            # Default location
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            challenges_file = os.path.join(curr_dir, '..', 'resources', 'challenges.json')
        
        self.challenges_file = challenges_file
        self.challenges = []
        self.load_challenges()

    def load_challenges(self):
        if not os.path.exists(self.challenges_file):
            return
            
        with open(self.challenges_file, 'r') as f:
            data = json.load(f)
            self.challenges = [Challenge.from_dict(c) for c in data]

    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        for c in self.challenges:
            if c.id == challenge_id:
                return c
        return None

    def verify(self, challenge_id: str, current_state: np.ndarray) -> Dict[str, Any]:
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return {"status": "error", "message": "Challenge not found"}
        
        f = calculate_fidelity(challenge.target_state, current_state)
        
        passed = f > 0.999 # Allow small numerical errors
        
        if passed:
            return {
                "status": "success",
                "fidelity": f,
                "message": f"Congratulations! Fidelity: {f*100:.2f}%"
            }
        else:
            return {
                "status": "fail",
                "fidelity": f,
                "message": f"Fidelity too low ({f*100:.2f}%). Check your circuit!"
            }
