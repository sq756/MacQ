"""
Q-Lang Code Editor Widget
Text editor for Q-Lang quantum circuit description with syntax highlighting
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                               QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
                          QTextDocument)
import re


class QLangHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Q-Lang"""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        
        # Define formats
        self.formats = {}
        
        # Gate names - bold blue
        gate_format = QTextCharFormat()
        gate_format.setForeground(QColor("#4A90E2"))
        gate_format.setFontWeight(QFont.Bold)
        self.formats['gate'] = gate_format
        
        # Numbers - green
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#27AE60"))
        self.formats['number'] = number_format
        
        # Comments - gray italic
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#999999"))
        comment_format.setFontItalic(True)
        self.formats['comment'] = comment_format
        
        # Operators - purple
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#9B59B6"))
        self.formats['operator'] = operator_format
        
        # Parameters - orange
        param_format = QTextCharFormat()
        param_format.setForeground(QColor("#E67E22"))
        self.formats['parameter'] = param_format
        
        # Define patterns
        self.patterns = [
            (r'\b[A-Z][A-Za-z†]*\b', 'gate'),  # Gate names
            (r'\bmeasure\b', 'gate'),  # measure keyword (v2.0)
            (r'\bif\b|\bthen\b|\band\b|\bor\b', 'gate'),  # Control flow keywords (v2.0)
            (r'\d+', 'number'),  # Numbers
            (r'#[^\n]*', 'comment'),  # Comments
            (r'[;,\-]|->|==', 'operator'),  # Operators (added -> and ==)
            (r'\([^)]+\)', 'parameter'),  # Parameters
            (r'[a-z][a-z0-9_]*', 'parameter'),  # Classical bit identifiers (v2.0)
        ]
    
    def highlightBlock(self, text):
        """Highlight a single block of text"""
        for pattern, format_name in self.patterns:
            regex = re.compile(pattern)
            for match in regex.finditer(text):
                start = match.start()
                length = len(match.group())
                self.setFormat(start, length, self.formats[format_name])


class QLangEditorWidget(QWidget):
    """Q-Lang code editor with compile functionality"""
    
    # Signal emitted when code is compiled successfully
    code_compiled = Signal(list)  # List of gate dicts
    qubit_count_detected = Signal(int)  # Detected qubit count from directive
    
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(400)
        self.setMaximumWidth(600)
        
        self._init_ui()
        
        # Q-Lang components
        from macq.qlang import QLangParser
        from macq.qlang.validator import QLangValidator, ValidationError
        from macq.qlang.compiler import QLangCompiler, QLangDecompiler
        
        self.parser = QLangParser()
        self.compiler = QLangCompiler()
        self.decompiler = QLangDecompiler()
        self.validator = None  # Will be set based on qubit count
        
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("⚛️ Q-Lang Editor")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                padding: 8px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 8px;
            }
        """)
        layout.addWidget(title)
        
        # Code editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Monaco", 12))
        self.editor.setPlaceholderText(
            "# Q-Lang v2.0: Now with measurements and conditionals!\n"
            "# Bell state:\n"
            "H 0\n"
            "CNOT 0-1\n"
            "measure 0 -> c0\n"
            "measure 1 -> c1"
        )
        self.editor.setStyleSheet("""
            QTextEdit {
                background: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        
        # Add syntax highlighting
        self.highlighter = QLangHighlighter(self.editor.document())
        
        layout.addWidget(self.editor,1)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        # Compile button
        self.compile_btn = QPushButton("▶ Compile")
        self.compile_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5AA0F2, stop:1 #458ACD);
            }
            QPushButton:pressed {
                background: #357ABD;
            }
        """)
        self.compile_btn.clicked.connect(self.compile_code)
        button_layout.addWidget(self.compile_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #E74C3C;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #C0392B;
            }
        """)
        self.clear_btn.clicked.connect(self.editor.clear)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7F8C8D;
                font-size: 11px;
                padding: 5px;
                background: #ECF0F1;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.status_label)
    
    def set_qubit_count(self, num_qubits: int):
        """Set the number of qubits for validation"""
        from macq.qlang.validator import QLangValidator
        self.validator = QLangValidator(num_qubits)
    
    def set_code(self, code: str):
        """Set editor content"""
        self.editor.setPlainText(code)
    
    def get_code(self) -> str:
        """Get editor content"""
        return self.editor.toPlainText()
    
    def compile_code(self):
        """Compile Q-Lang code to gates"""
        code = self.get_code()
        
        if not code.strip():
            self._show_error("Empty code", "Please enter some Q-Lang code first")
            return
        
        try:
            # Parse
            self.status_label.setText("Parsing...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #F39C12;
                    font-size: 11px;
                    padding: 5px;
                    background: #FEF5E7;
                    border-radius: 4px;
                }
            """)
            ast = self.parser.parse(code)
            
            # Check for qubit count directive
            if ast.num_qubits is not None:
                self.qubit_count_detected.emit(ast.num_qubits)
                # Re-initialize validator with new count
                self.set_qubit_count(ast.num_qubits)
            
            # Validate (if validator is set)
            if self.validator:
                self.status_label.setText("Validating...")
                self.validator.validate(ast)
            
            # Compile
            self.status_label.setText("Compiling...")
            gates = self.compiler.compile(ast)
            
            # Success
            self.status_label.setText(f"✅ Compiled {len(gates)} gates successfully!")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #27AE60;
                    font-size: 11px;
                    padding: 5px;
                    background: #D5F4E6;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
            
            # Emit signal
            self.code_compiled.emit(gates)
            
        except SyntaxError as e:
            self._show_error("Syntax Error", str(e))
        except Exception as e:
            self._show_error("Error", str(e))
    
    def _show_error(self, title: str, message: str):
        """Show error message"""
        self.status_label.setText(f"❌ {title}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #E74C3C;
                font-size: 11px;
                padding: 5px;
                background: #FADBD8;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        QMessageBox.critical(self, title, message)


# Test standalone
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    editor = QLangEditorWidget()
    editor.setWindowTitle("Q-Lang Editor Test")
    editor.set_qubit_count(5)
    
    # Set example code
    example_code = """# Bell state
H 0
CNOT 0-1
"""
    editor.set_code(example_code)
    
    # Connect signal
    def on_compiled(gates):
        print("Compiled gates:")
        for gate in gates:
            print(f"  {gate}")
    
    editor.code_compiled.connect(on_compiled)
    
    editor.show()
    sys.exit(app.exec())
