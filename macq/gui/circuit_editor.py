"""
MacQ GUI - Circuit Editor Widget (Restored & Enhanced)
Visual quantum circuit editor with drag-and-drop, selection, and macros.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu, QSizePolicy, QMessageBox, QInputDialog
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QAction

from ..c_bridge import QuantumState
from .styles import CIRCUIT_EDITOR_STYLE

class CircuitEditorWidget(QWidget):
    circuit_changed = Signal()
    gate_added = Signal(str, int)
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(450, 350)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(CIRCUIT_EDITOR_STYLE)
        
        self.num_qubits = 3
        self.gates = []
        self.qubit_spacing = 80
        self.gate_width = 50
        self.time_step_width = 70
        
        # Selection state
        self.selection_start = None
        self.selection_end = None
        self.selected_gate_indices = []
        self.macros = {}
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def set_qubit_count(self, count):
        self.num_qubits = count
        self.gates = []
        self._update_size()
        self.update()
        self.circuit_changed.emit()

    def get_qubit_count(self): return self.num_qubits
    def get_gate_count(self): return len(self.gates)
    def clear_circuit(self):
        self.gates = []
        self._update_size()
        self.update()
        self.circuit_changed.emit()

    def add_gate(self, gate_type, qubit, time_step=None, control=None):
        if time_step is None:
            time_step = self._next_available_time_step(qubit)
        
        new_gate = {
            'type': gate_type,
            'qubit': qubit,
            'time_step': time_step,
            'control': control
        }
        self.gates.append(new_gate)
        self._update_size()
        self.update()
        self.gate_added.emit(gate_type, qubit)
        self.circuit_changed.emit()

    def _next_available_time_step(self, qubit):
        max_step = -1
        for gate in self.gates:
            if gate['qubit'] == qubit or gate.get('control') == qubit:
                max_step = max(max_step, gate['time_step'])
        return max_step + 1

    def _update_size(self):
        max_step = max([g['time_step'] for g in self.gates]) if self.gates else 0
        width = max(800, 150 + max_step * self.time_step_width)
        height = max(400, 100 + self.num_qubits * self.qubit_spacing)
        self.setFixedSize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0F111A"))
        
        # Draw lines
        pen = QPen(QColor("#4A90E2"), 2)
        for i in range(self.num_qubits):
            y = 50 + i * self.qubit_spacing
            painter.setPen(QPen(QColor("#2E344B"), 1))
            painter.drawLine(60, y, self.width(), y)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(10, y-10, 40, 20, Qt.AlignCenter, f"q{i}")
            
        # Draw gates
        for idx, gate in enumerate(self.gates):
            gt = gate['type']
            q = gate['qubit']
            ts = gate['time_step']
            ctrl = gate.get('control')
            
            x = 80 + ts * self.time_step_width
            y = 50 + q * self.qubit_spacing
            
            # Highlight if selected
            if idx in self.selected_gate_indices:
                painter.setPen(QPen(QColor(255, 255, 0), 2))
                painter.drawRect(x-28, y-25, 56, 50)
            
            # Simple gate box
            color = QColor("#4A90E2") if gt == 'H' else QColor("#E24A4A")
            painter.setBrush(color)
            painter.setPen(QPen(color.darker(), 1))
            painter.drawRoundedRect(x-25, y-20, 50, 40, 5, 5)
            painter.setPen(QColor("white"))
            painter.drawText(x-25, y-20, 50, 40, Qt.AlignCenter, gt)
            
            if ctrl is not None:
                cy = 50 + ctrl * self.qubit_spacing
                painter.setPen(QPen(QColor("#4A90E2"), 2))
                painter.drawLine(x, cy, x, y)
                painter.drawEllipse(x-5, cy-5, 10, 10)

        # Draw selection rectangle
        if self.selection_start and self.selection_end:
            rect = QRect(self.selection_start, self.selection_end).normalized()
            painter.setPen(QPen(QColor(74, 144, 226, 200), 1, Qt.DashLine))
            painter.setBrush(QColor(74, 144, 226, 40))
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selection_start = event.pos()
            self.selection_end = event.pos()
            self.selected_gate_indices = []
            self.update()
        elif event.button() == Qt.RightButton:
            if self.selected_gate_indices:
                self._show_selection_menu(event.pos())
            else:
                self._show_context_menu(event.pos())

    def mouseMoveEvent(self, event):
        if self.selection_start:
            self.selection_end = event.pos()
            self._update_selection()
            self.update()

    def mouseReleaseEvent(self, event):
        self.selection_start = None
        self.selection_end = None
        self.update()

    def _update_selection(self):
        rect = QRect(self.selection_start, self.selection_end).normalized()
        self.selected_gate_indices = []
        for i, gate in enumerate(self.gates):
            x = 80 + gate['time_step'] * self.time_step_width
            y = 50 + gate['qubit'] * self.qubit_spacing
            if rect.intersects(QRect(x-25, y-20, 50, 40)):
                self.selected_gate_indices.append(i)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        qubit = min(int((pos.y() - 20) / self.qubit_spacing), self.num_qubits - 1)
        menu.addAction(f"Add H to q{qubit}").triggered.connect(lambda: self.add_gate('H', qubit))
        menu.addAction(f"Add X to q{qubit}").triggered.connect(lambda: self.add_gate('X', qubit))
        menu.exec(self.mapToGlobal(pos))

    def _show_selection_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("📦 Pack into Gate").triggered.connect(self._pack_selection)
        menu.addAction("🗑️ Delete Selected").triggered.connect(self._delete_selection)
        menu.exec(self.mapToGlobal(pos))

    def _pack_selection(self):
        name, ok = QInputDialog.getText(self, "Macro", "Name:")
        if ok and name:
            self.macros[name] = [self.gates[i] for i in sorted(self.selected_gate_indices)]
            QMessageBox.information(self, "Success", f"Macro '{name}' created.")
            self.selected_gate_indices = []
            self.update()

    def _delete_selection(self):
        for i in sorted(self.selected_gate_indices, reverse=True):
            self.gates.pop(i)
        self.selected_gate_indices = []
        self.circuit_changed.emit()
        self.update()
