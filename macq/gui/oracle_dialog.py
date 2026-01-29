from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QFormLayout,
    QMessageBox
)
from PySide6.QtCore import Signal
from ..core.oracle import OracleBuilder

class OracleDialog(QDialog):
    # Signal emitted when gates are generated, carrying the list of gates
    gates_generated = Signal(list)

    def __init__(self, qubit_count: int, parent=None):
        super().__init__(parent)
        self.qubit_count = qubit_count
        self.setWindowTitle("🔮 Oracle Builder")
        self.setMinimumWidth(400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        info = QLabel("Enter a boolean expression using Python operators (&, |, ^, ~).\n"
                      "Example: (a & b) ^ c")
        info.setStyleSheet("color: #A0A0A0; margin-bottom: 10px;")
        layout.addWidget(info)
        
        form = QFormLayout()
        
        self.expr_input = QLineEdit("(q0 & q1)")
        self.expr_input.setPlaceholderText("e.g., (q0 & q1) ^ q2")
        form.addRow("Expression:", self.expr_input)
        
        self.inputs_input = QLineEdit("q0, q1")
        self.inputs_input.setPlaceholderText("Comma separated qubit names used in expression")
        form.addRow("Inputs:", self.inputs_input)
        
        self.target_input = QComboBox()
        for i in range(self.qubit_count):
            self.target_input.addItem(f"q{i}", i)
        form.addRow("Target Qubit:", self.target_input)
        
        layout.addLayout(form)
        
        # Buttons
        btns = QHBoxLayout()
        self.compile_btn = QPushButton("Compile into Gates")
        self.compile_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background: #357ABD; }
        """)
        self.compile_btn.clicked.connect(self._on_compile)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(self.compile_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

    def _on_compile(self):
        expr = self.expr_input.text()
        inputs = [s.strip() for s in self.inputs_input.text().split(",") if s.strip()]
        target_idx = self.target_input.currentData()
        target_name = self.target_input.currentText()
        
        if not expr or not inputs:
            QMessageBox.warning(self, "Invalid Input", "Please provide expression and inputs.")
            return
            
        try:
            # Generate gates using core logic
            # Mapper to convert names to indices for the actual gate addition
            generated_gates = OracleBuilder.build_from_expression(expr, inputs, target_name)
            
            # Convert name-based gates to index-based for the circuit editor
            final_gates = []
            name_to_idx = {name: int(name[1:]) for name in inputs if name.startswith('q')}
            # Also handle the target
            name_to_idx[target_name] = target_idx
            
            for g in generated_gates:
                if g['type'] == 'X':
                    q_idx = int(g['qubits'][0][1:])
                    final_gates.append({'type': 'X', 'qubit': q_idx})
                elif g['type'] == 'MCX':
                    controls = [int(n[1:]) for n in g['controls']]
                    final_gates.append({'type': 'Toffoli', 'qubits': controls + [target_idx]})
            
            if final_gates:
                self.gates_generated.emit(final_gates)
                self.accept()
            else:
                QMessageBox.information(self, "Empty Oracle", "The expression does not yield any gates (always 0).")
                
        except Exception as e:
            QMessageBox.critical(self, "Compilation Error", f"Failed to compile oracle: {e}")
