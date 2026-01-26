"""
MacQ GUI - Circuit Editor Widget
Visual quantum circuit editor with drag-and-drop support
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont

from ..c_bridge import QuantumState


class CircuitEditorWidget(QWidget):
    """量子电路编辑器"""
    
    circuit_changed = Signal()
    gate_added = Signal(str, int)  # gate_type, qubit
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setAcceptDrops(True)
        
        self.num_qubits = 3
        self.gates = []  # [(gate_type, qubit, time_step, params), ...]
        self.qubit_spacing = 80
        self.gate_width = 50
        self.time_step_width = 70
        
        # Background
        self.setStyleSheet("background-color: white;")
        
    def set_qubit_count(self, count):
        """设置量子比特数量"""
        self.num_qubits = count
        self.gates = []  # 清空电路
        self.update()
        self.circuit_changed.emit()
        
    def get_qubit_count(self):
        """获取量子比特数量"""
        return self.num_qubits
    
    def get_gate_count(self):
        """获取门数量"""
        return len(self.gates)
    
    def clear_circuit(self):
        """清空电路"""
        self.gates = []
        self.update()
        self.circuit_changed.emit()
    
    def add_gate(self, gate_type, qubit, time_step=None):
        """添加门到电路"""
        if time_step is None:
            # 自动找到下一个可用的time_step
            time_step = self._next_available_time_step(qubit)
        
        self.gates.append({
            'type': gate_type,
            'qubit': qubit,
            'time_step': time_step,
            'params': {}
        })
        
        self.update()
        self.gate_added.emit(gate_type, qubit)
        self.circuit_changed.emit()
    
    def _next_available_time_step(self, qubit):
        """找到下一个可用的time_step"""
        occupied = [g['time_step'] for g in self.gates if g['qubit'] == qubit]
        if not occupied:
            return 0
        return max(occupied) + 1
    
    def execute_circuit(self):
        """执行电路并返回量子态"""
        if not self.gates:
            return None
        
        # 创建量子态
        qs = QuantumState(self.num_qubits)
        
        # 按time_step排序门
        sorted_gates = sorted(self.gates, key=lambda g: g['time_step'])
        
        # 执行每个门
        for gate in sorted_gates:
            gate_type = gate['type']
            qubit = gate['qubit']
            
            try:
                # 单量子比特门
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
                # TODO: 添加更多门
                
            except Exception as e:
                print(f"Error applying gate {gate_type}: {e}")
        
        return qs
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """放置事件"""
        gate_type = event.mimeData().text()
        pos = event.pos()
        
        # 计算放置的量子比特
        qubit = min(int(pos.y() / self.qubit_spacing), self.num_qubits - 1)
        
        # 添加门
        self.add_gate(gate_type, qubit)
        
        event.acceptProposedAction()
    
    def paintEvent(self, event):
        """绘制电路"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制量子比特线
        self._draw_qubit_lines(painter)
        
        # 绘制门
        self._draw_gates(painter)
    
    def _draw_qubit_lines(self, painter):
        """绘制量子比特线"""
        pen = QPen(QColor("#CCCCCC"), 2)
        painter.setPen(pen)
        
        # 字体
        font = QFont("Arial", 12)
        painter.setFont(font)
        
        for i in range(self.num_qubits):
            y = 50 + i * self.qubit_spacing
            
            # 绘制标签
            painter.setPen(QColor("#333333"))
            painter.drawText(10, y + 5, f"q[{i}]")
            
            # 绘制线
            painter.setPen(pen)
            painter.drawLine(60, y, self.width() - 20, y)
    
    def _draw_gates(self, painter):
        """绘制所有门"""
        from .gate_palette import GatePaletteWidget
        colors = GatePaletteWidget.GATE_COLORS
        
        for gate in self.gates:
            gate_type = gate['type']
            qubit = gate['qubit']
            time_step = gate['time_step']
            
            # 计算位置
            x =80 + time_step * self.time_step_width
            y = 50 + qubit * self.qubit_spacing
            
            # 获取颜色
            color = QColor(colors.get(gate_type, '#95A5A6'))
            
            # 绘制门框
            painter.setBrush(color)
            painter.setPen(QPen(color.darker(120), 2))
            painter.drawRect(x - self.gate_width//2, y - 20, 
                           self.gate_width, 40)
            
            # 绘制门标签
            painter.setPen(QColor("white"))
            font = QFont("Arial", 11, QFont.Bold)
            painter.setFont(font)
            painter.drawText(x - self.gate_width//2, y - 20,
                           self.gate_width, 40,
                           Qt.AlignCenter, gate_type)
