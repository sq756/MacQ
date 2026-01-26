"""
MacQ Web Server - Flask Backend
Connects WebGL frontend to C quantum engine
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from macq import QuantumState

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for local development


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/app.js')
def app_js():
    return send_from_directory('.', 'app.js')


@app.route('/execute', methods=['POST'])
def execute_circuit():
    """Execute quantum circuit and return results"""
    try:
        data = request.json
        num_qubits = data.get('num_qubits', 3)
        gates = data.get('gates', [])
        
        # Create quantum state
        qs = QuantumState(num_qubits)
        
        # Apply gates
        for gate_info in gates:
            gate_type = gate_info['gate']
            qubit = gate_info['qubit']
            
            try:
                if gate_type == 'H':
                    qs.h(qubit)
                elif gate_type == 'X':
                    qs.x(qubit)
                elif gate_type == 'Y':
                    qs.y(qubit)
                elif gate_type == 'Z':
                    qs.z(qubit)
                elif gate_type == 'S':
                    qs.s(qubit)
                elif gate_type == 'T':
                    qs.t(qubit)
                elif gate_type == 'CNOT':
                    # Simple: use qubit and qubit+1
                    target = (qubit + 1) % num_qubits
                    qs.cnot(qubit, target)
                elif gate_type == 'CZ':
                    target = (qubit + 1) % num_qubits
                    qs.cz(qubit, target)
                elif gate_type == 'SWAP':
                    target = (qubit + 1) % num_qubits
                    qs.swap(qubit, target)
            except Exception as e:
                print(f"Error applying gate {gate_type}: {e}")
        
        # Get probabilities
        probs = qs.probabilities()
        
        # Calculate Bloch sphere coordinates for single qubit
        bloch_coords = None
        if num_qubits == 1:
            vec = qs.get_statevector()
            alpha = vec[0]
            beta = vec[1]
            
            # Calculate theta and phi from Bloch sphere representation
            theta = 2 * np.arccos(np.abs(alpha))
            phi = np.angle(beta) - np.angle(alpha)
            
            bloch_coords = {
                'theta': float(theta),
                'phi': float(phi)
            }
        
        return jsonify({
            'success': True,
            'probabilities': probs.tolist(),
            'bloch': bloch_coords,
            'state_vector': [{'real': c.real, 'imag': c.imag} 
                           for c in qs.get_statevector()]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'version': '1.0.0'})


if __name__ == '__main__':
    print("🚀 启动MacQ Web服务器...")
    print("📡 访问: http://localhost:8080")
    print("⚛️  3D量子可视化已就绪!")
    app.run(host='0.0.0.0', port=8080, debug=True)
