"""
MacQ GUI - Circuit Editor Widget
Visual quantum circuit editor with drag-and-drop support
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient

from ..c_bridge import QuantumState
from .styles import CIRCUIT_EDITOR_STYLE


class CircuitEditorWidget(QWidget):
    """量子电路编辑器 - Premium版本"""
    
    circuit_changed = Signal()
    gate_added = Signal(str, int)
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(450, 350)
        self.setAcceptDrops(True)
        
        # 应用Premium样式
        self.setStyleSheet(CIRCUIT_EDITOR_STYLE)
        
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
    
    def add_gate(self, gate_type, qubit, time_step=None, control=None):
        """添加门到电路"""
        if time_step is None:
            # 自动找到下一个可用的time_step
            time_step = self._next_available_time_step(qubit)
        
        # 检查是否是多量子比特门
        multi_qubit_gates = ['CNOT', 'CZ', 'SWAP', 'Toffoli']
        
        if gate_type in multi_qubit_gates and control is None:
            # 对于多量子比特门，如果没有指定控制位，选择前一个量子比特
            if gate_type == 'CNOT' or gate_type == 'CZ':
                control = qubit - 1 if qubit > 0 else qubit + 1
                if control >= self.num_qubits:
                    control = 0
            elif gate_type == 'SWAP':
                # SWAP需要两个量子比特，选择相邻的
                control = qubit - 1 if qubit > 0 else qubit + 1
                if control >= self.num_qubits:
                    return  # 无法添加
        
        self.gates.append({
            'type': gate_type,
            'qubit': qubit,
            'control': control,
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
            control = gate.get('control')
            
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
                elif gate_type == 'I':
                    pass  # 单位门不做任何操作
                
                # 双量子比特门
                elif gate_type == 'CNOT' and control is not None:
                    qs.cnot(control, qubit)
                elif gate_type == 'CZ' and control is not None:
                    qs.cz(control, qubit)
                elif gate_type == 'SWAP' and control is not None:
                    qs.swap(control, qubit)
                
                # 三量子比特门
                elif gate_type == 'Toffoli' and control is not None:
                    # 简化：使用qubit-2, qubit-1作为控制位
                    if qubit >= 2:
                        qs.toffoli(qubit-2, qubit-1, qubit)
                
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
            control = gate.get('control')
            
            # 计算位置
            x = 80 + time_step * self.time_step_width
            y = 50 + qubit * self.qubit_spacing
            
            # 获取颜色
            color = QColor(colors.get(gate_type, '#95A5A6'))
            
            # 如果是多量子比特门，先绘制控制线
            if control is not None and gate_type in ['CNOT', 'CZ', 'SWAP']:
                control_y = 50 + control * self.qubit_spacing
                
                # 绘制竖线连接控制位和目标位
                painter.setPen(QPen(QColor("#333333"), 3))
                painter.drawLine(x, control_y, x, y)
                
                # 绘制控制点（小圆圈）
                painter.setBrush(QColor("#333333"))
                painter.drawEllipse(x - 6, control_y - 6, 12, 12)
                
                # CNOT的目标点（⊕符号）
                if gate_type == 'CNOT':
                    painter.setBrush(Qt.NoBrush)
                    painter.setPen(QPen(color, 3))
                    painter.drawEllipse(x - 20, y - 20, 40, 40)
                    painter.drawLine(x - 15, y, x + 15, y)
                    painter.drawLine(x, y - 15, x, y + 15)
                    continue  # CNOT不绘制方框
                
                elif gate_type == 'SWAP':
                    # SWAP用X符号
                    painter.setPen(QPen(color, 3))
                    painter.drawLine(x - 10, control_y - 10, x + 10, control_y + 10)
                    painter.drawLine(x - 10, control_y + 10, x + 10, control_y - 10)
                    painter.drawLine(x - 10, y - 10, x + 10, y + 10)
                    painter.drawLine(x - 10, y + 10, x + 10, y - 10)
                    continue
            
            # 绘制普通门框
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
