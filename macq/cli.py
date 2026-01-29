#!/usr/bin/env python3
"""
MacQ CLI - Command Line Interface for MacQ Quantum Simulator
Supports headless execution, optimization, and analysis of Q-Lang scripts.
"""

import sys
import argparse
import json
import time
from macq import Circuit, QuantumState, DensityMatrix, version

def cmd_run(args):
    """Run a Q-Lang script and output results."""
    try:
        # Read code from file or stdin
        if args.file == '-':
            code = sys.stdin.read()
        else:
            with open(args.file, 'r') as f:
                code = f.read()
        
        start_time = time.time()
        
        # 1. Parse and build circuit
        circuit = Circuit.from_qlang(code)
        parse_time = time.time() - start_time
        
        # 2. Execute simulation
        sim_start = time.time()
        state = circuit.execute(noise_level=args.noise)
        sim_time = time.time() - sim_start
        
        total_time = time.time() - start_time
        
        # 3. Collect measurements if shots > 0
        counts = {}
        if args.shots > 0:
            counts = state.sample_counts(args.shots)
        
        # 4. Prepare output
        results = {
            "version": version(),
            "status": "success",
            "metadata": {
                "num_qubits": circuit.num_qubits,
                "gate_count": len(circuit.gates),
                "noise_level": args.noise,
                "shots": args.shots
            },
            "performance": {
                "parse_time_sec": parse_time,
                "simulation_time_sec": sim_time,
                "total_time_sec": total_time
            },
            "results": {
                "counts": counts
            }
        }
        
        if args.statevector:
            vec = state.get_statevector()
            results["results"]["statevector"] = [
                {"real": float(c.real), "imag": float(c.imag)} for c in vec
            ]
            
        # 5. Output format
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        elif args.format == 'csv':
            if not counts:
                print("state,count")
            else:
                print("state,count")
                for s, c in sorted(counts.items()):
                    print(f"{s},{c}")
        else: # Text
            print(f"--- MacQ Simulation Result ---")
            print(f"Qubits: {circuit.num_qubits} | Gates: {len(circuit.gates)}")
            print(f"Time: {total_time:.4f}s (Sim: {sim_time:.4f}s)")
            if counts:
                print(f"\nMeasurement Counts ({args.shots} shots):")
                for s, c in sorted(counts.items()):
                    print(f"  |{s}> : {c}")
            else:
                print("\nNo measurements performed (shots=0).")
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_optimize(args):
    """Optimize a Q-Lang script and output the simplified code."""
    try:
        with open(args.file, 'r') as f:
            code = f.read()
        
        circuit = Circuit.from_qlang(code)
        from macq.core.optimizer import CircuitOptimizer
        optimizer = CircuitOptimizer()
        
        before = len(circuit.gates)
        optimizer.optimize(circuit)
        after = len(circuit.gates)
        
        new_code = circuit.to_qlang()
        
        if args.inplace:
            with open(args.file, 'w') as f:
                f.write(new_code)
            print(f"Optimized: {before} -> {after} gates (Written to {args.file})")
        else:
            print(new_code)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_analyze(args):
    """Analyze circuit properties (Hamiltonian, Density Matrix)."""
    try:
        with open(args.file, 'r') as f:
            code = f.read()
            
        circuit = Circuit.from_qlang(code)
        state = circuit.execute()
        dm = DensityMatrix.from_statevector(state)
        
        analysis = {
            "num_qubits": circuit.num_qubits,
            "gate_count": len(circuit.gates),
            "purity": float(np.real(dm.to_numpy().trace())), # Just a placeholder analysis
            # In a real tool, we might output the full matrix or entropy
        }
        
        print(json.dumps(analysis, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="MacQ Quantum Simulator CLI")
    parser.add_argument('-v', '--version', action='version', version=f'MacQ CLI {version()}')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run Command
    run_parser = subparsers.add_parser('run', help='Execute a Q-Lang script')
    run_parser.add_argument('file', help='Path to .ql file or - for stdin')
    run_parser.add_argument('-s', '--shots', type=int, default=1024, help='Number of shots for measurement')
    run_parser.add_argument('-n', '--noise', type=float, default=0.0, help='Noise level (0.0 to 1.0)')
    run_parser.add_argument('--statevector', action='store_true', help='Output full statevector')
    run_parser.add_argument('-f', '--format', choices=['json', 'csv', 'text'], default='text', help='Output format')
    
    # Optimize Command
    opt_parser = subparsers.add_parser('optimize', help='Simplify a Q-Lang script')
    opt_parser.add_argument('file', help='Path to .ql file')
    opt_parser.add_argument('-i', '--inplace', action='store_true', help='Update file in-place')
    
    # Analyze Command
    ana_parser = subparsers.add_parser('analyze', help='Extract circuit properties')
    ana_parser.add_argument('file', help='Path to .ql file')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        cmd_run(args)
    elif args.command == 'optimize':
        cmd_optimize(args)
    elif args.command == 'analyze':
        cmd_analyze(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    import numpy as np # Needed for analysis calculations
    main()
