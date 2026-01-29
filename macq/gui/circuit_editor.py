"""
MacQ GUI - Circuit Editor Widget
Visual quantum circuit editor with drag-and-drop support
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QAction

from ..c_bridge import QuantumState
from .styles import CIRCUIT_EDITOR_STYLE


class CircuitEditorWidget(QWidget):
    """量子电路编辑器 - Premium版本"""
    
    circuit_changed = Signal()
    gate_added = Signal(str, int)
    
    # 可用的门类型
    AVAILABLE_GATES = {
        '基础门': ['H', 'X', 'Y', 'Z', 'I'],
        '相位门': ['S', 'T'],
        '双比特门': ['CNOT', 'CZ', 'SWAP'],
        '多比特门': ['Toffoli']
    }
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(450, 350)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 应用Premium样式
        self.setStyleSheet(CIRCUIT_EDITOR_STYLE)
        
        self.num_qubits = 3
        self.gates = []  # [(gate_type, qubit, time_step, params), ...]
        self.qubit_spacing = 80
        self.gate_width = 50
        self.time_step_width = 70
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, pos):
        """显示右键菜单选择门"""
        # 计算点击的量子比特
        qubit = min(int((pos.y() - 20) / self.qubit_spacing), self.num_qubits - 1)
        if qubit < 0:
            return
        
        # 创建菜单
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(30, 34, 55, 0.95);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 8px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 30px;
                border-radius: 4px;
                color: #E8E8E8;
            }
            QMenu::item:selected {
                background: rgba(74, 144, 226, 0.4);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255, 255, 255, 0.1);
                margin: 4px 0;
            }
        """)
        
        # 添加标题
        title = menu.addAction(f"⚛️ 添加门到 q{qubit}")
        title.setEnabled(False)
        menu.addSeparator()
        
        # 分类添加门
        for category, gates in self.AVAILABLE_GATES.items():
            category_menu = menu.addMenu(category)
            for gate_name in gates:
                action = category_menu.addAction(gate_name)
                action.triggered.connect(lambda checked, g=gate_name, q=qubit: self.add_gate(g, q))
        
        # 显示菜单
        menu.exec(self.mapToGlobal(pos))
    
    def _update_size(self):
        """Update widget size to trigger scrollbars"""
        hint = self.sizeHint()
        # Use setFixedSize to force the scroll area to show scrollbars
        self.setFixedSize(hint)
        self.updateGeometry()

    def set_qubit_count(self, count):
        """设置量子比特数量"""
        self.num_qubits = count
        self.gates = []  # 清空电路
        self._update_size()
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
        self._update_size()
        self.update()
        self.circuit_changed.emit()
    
    def clear_circuit(self):
        """清空电路"""
        self.gates = []
        self._update_size()
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
        
        self._update_size()
        self.update()
        self.gate_added.emit(gate_type, qubit)
        self.circuit_changed.emit()
    
    def optimize_circuit(self):
        """优化电路：使用核心优化引擎简化门操作"""
        if not self.gates: return
        
        from ..core.optimizer import CircuitOptimizer
        optimized_gates = CircuitOptimizer.simplify_pauli_strings(self.gates, self.num_qubits)
        
        # 更新显示用的门列表
        self.gates = optimized_gates
        self._update_size()
        self.update()
        self.circuit_changed.emit()
    
    def sizeHint(self):
        """计算推荐大小"""
        max_ts = 0
        if self.gates:
            max_ts = max(g['time_step'] for g in self.gates)
        
        # 增加一些边缘留白 (Margin)
        width = max(800, 300 + (max_ts + 2) * self.time_step_width)
        height = max(600, 150 + self.num_qubits * self.qubit_spacing)
        return QSize(width, height)
        
    def minimumSizeHint(self):
        return self.sizeHint()
    
    def _next_available_time_step(self, qubit):
        """找到下一个可用的time_step"""
        occupied = [g['time_step'] for g in self.gates if g['qubit'] == qubit]
        if not occupied:
            return 0
        return max(occupied) + 1
    
    def execute_circuit(self, initial_state=None, noise_level=0.0):
        """执行电路并返回量子态，支持噪声模型"""
        if not self.gates:
            return initial_state
        
        # 创建或使用初始量子态
        qs = initial_state if initial_state else QuantumState(self.num_qubits)
        
        # 按time_step排序门
        sorted_gates = sorted(self.gates, key=lambda g: g['time_step'])
        
        # 执行每个门
        for gate in sorted_gates:
            gate_type = gate['type']
            qubit = gate['qubit']
            control = gate.get('control')
            control2 = gate.get('control2')
            params = gate.get('params', {})
            
            applied = False
            try:
                # 1. Single Qubit Gates
                if gate_type == 'H':
                    qs.h(qubit)
                    applied = True
                elif gate_type == 'X':
                    qs.x(qubit)
                    applied = True
                elif gate_type == 'Y':
                    qs.y(qubit)
                    applied = True
                elif gate_type == 'Z':
                    qs.z(qubit)
                    applied = True
                elif gate_type == 'S':
                    qs.s(qubit)
                    applied = True
                elif gate_type == 'T':
                    qs.t(qubit)
                    applied = True
                
                # 2. Rotation Gates
                elif gate_type in ['Rx', 'Ry', 'Rz']:
                    angle = params.get('angle', 0.0)
                    if isinstance(angle, str):
                        import math
                        angle = angle.replace('π', 'math.pi').replace('pi', 'math.pi')
                        try:
                            angle = eval(angle, {"math": math, "np": np})
                        except:
                            angle = 0.0
                    
                    if gate_type == 'Rx': qs.rx(qubit, angle)
                    elif gate_type == 'Ry': qs.ry(qubit, angle)
                    elif gate_type == 'Rz': qs.rz(qubit, angle)
                    applied = True
                
                # 3. Two-Qubit Gates
                elif gate_type == 'CNOT' and control is not None:
                    qs.cnot(control, qubit)
                    applied = True
                elif gate_type == 'CZ' and control is not None:
                    qs.cz(control, qubit)
                    applied = True
                elif gate_type == 'SWAP' and control is not None:
                    qs.swap(control, qubit)
                    applied = True
                
                # 4. Three-Qubit Gates
                elif gate_type == 'Toffoli':
                    c1 = control
                    c2 = control2
                    if c2 is None and qubit >= 2: # Fallback
                        c1, c2 = qubit-2, qubit-1
                    if c1 is not None and c2 is not None:
                        qs.toffoli(c1, c2, qubit)
                        applied = True
                
                # 5. v2.0 & Complex Gates
                elif gate_type == 'MEASURE':
                    qs.measure(qubit)
                    applied = True
                elif gate_type in ['QFT', 'QFT_INV']:
                    q_list = params.get('qubits', list(range(self.num_qubits)))
                    qs.qft(q_list, inverse=(gate_type == 'QFT_INV'))
                    applied = True
                elif gate_type == 'MOD_EXP':
                    a = params.get('a', 2)
                    N = params.get('N', 15)
                    ctrls = params.get('controls', [])
                    tgts = params.get('targets', [])
                    if ctrls and tgts:
                        qs.mod_exp(a, N, ctrls, tgts)
                        applied = True

                # Noise Injection
                if applied and noise_level > 0:
                    # Apply noise to all participating qubits
                    qs.apply_depolarizing(qubit, noise_level * 0.5)
                    qs.apply_amplitude_damping(qubit, noise_level * 0.5)
                    if control is not None:
                        qs.apply_depolarizing(control, noise_level * 0.5)
                    if control2 is not None:
                        qs.apply_depolarizing(control2, noise_level * 0.5)

            except Exception as e:
                print(f"Error applying gate {gate_type} on q{qubit}: {e}")
        
        return qs
    
    def get_circuit_unitary(self):
        """计算当前电路的完整幺正矩阵（哈密顿量相关）"""
        size = 2 ** self.num_qubits
        import numpy as np
        matrix = np.zeros((size, size), dtype=np.complex128)
        
        for i in range(size):
            # 创建对应基态的初始态
            qs = QuantumState(self.num_qubits)
            bitstring = bin(i)[2:].zfill(self.num_qubits)[::-1]
            qs.init_basis(bitstring)
            
            # 运行电路
            final_qs = self.execute_circuit(initial_state=qs)
            
            # 提取结果向量作为矩阵的一列
            matrix[:, i] = final_qs.get_statevector()
            
        return matrix
    
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
        
        # 绘制背景 (手动绘制以确保滚动时背景跟随)
        painter.fillRect(self.rect(), QColor("#0F111A"))
        
        # 绘制量子比特线
        self._draw_qubit_lines(painter)
        
        # 绘制门
        self._draw_gates(painter)
    
    def _draw_qubit_lines(self, painter):
        """绘制量子比特线"""
        pen = QPen(QColor("#4A90E2"), 2)
        painter.setPen(pen)
        
        # 字体
        font = QFont(".AppleSystemUIFont", 13)
        font.setBold(True)
        painter.setFont(font)
        
        for i in range(self.num_qubits):
            y = 50 + i * self.qubit_spacing
            
            # 绘制标签背景
            painter.setBrush(QColor(74, 144, 226, 50))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(5, y - 15, 50, 30, 6, 6)
            
            # 绘制标签文字
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(10, y - 15, 40, 30, Qt.AlignCenter, f"q{i}")
            
            # 绘制线 - 更亮的颜色
            painter.setPen(QPen(QColor("#667eea"), 3, Qt.DotLine))
            painter.drawLine(60, y, self.width() - 20, y)
    
    def _draw_gates(self, painter):
        """绘制所有门 - Premium版本"""
        from .gate_palette import GatePaletteWidget
        colors = GatePaletteWidget.GATE_COLORS
        
        painter.setRenderHint(QPainter.Antialiasing, True)
        
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
            
            # ============================================================
            # V2.0 Gates: MEASURE, MOD_EXP, QFT
            # ============================================================
            
            # MEASURE gate - Special meter icon
            if gate_type == 'MEASURE':
                classical_bit = gate.get('params', {}).get('classical_bit', 'c?')
                
                # Draw meter box
                painter.setBrush(QColor("#E74C3C"))
                painter.setPen(QPen(QColor("#C0392B"), 2))
                painter.drawRoundedRect(x - 25, y - 20, 50, 40, 8, 8)
                
                # Draw meter arc
                painter.setPen(QPen(QColor("#FFFFFF"), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawArc(x - 15, y - 10, 30, 20, 0, 180 * 16)
                
                # Draw needle
                painter.drawLine(x, y, x + 8, y - 8)
                
                # Draw classical bit label
                painter.setPen(QColor("#FFFFFF"))
                font = QFont("SF Pro Display", 9, QFont.Bold)
                painter.setFont(font)
                painter.drawText(x - 25, y + 12, 50, 15, Qt.AlignCenter, f"→{classical_bit}")
                continue
            
            # MOD_EXP gate - Multi-qubit modular operation
            if gate_type in ['MOD_EXP', 'MOD_ADD', 'MOD_MUL']:
                params = gate.get('params', {})
                control_qubits = params.get('control_qubits', [])
                target_qubits = params.get('target_qubits', [])
                base = params.get('base', '?')
                modulus = params.get('modulus', '?')
                
                if control_qubits and target_qubits:
                    # Calculate bounding box
                    all_qubits = control_qubits + target_qubits
                    min_qubit = min(all_qubits)
                    max_qubit = max(all_qubits)
                    
                    top_y = 50 + min_qubit * self.qubit_spacing
                    bottom_y = 50 + max_qubit * self.qubit_spacing
                    height = bottom_y - top_y + 40
                    
                    # Draw connector box
                    painter.setBrush(QColor(155, 89, 182, 40))
                    painter.setPen(QPen(QColor("#9B59B6"), 3, Qt.DashLine))
                    painter.drawRoundedRect(x - 35, top_y - 20, 70, height, 12, 12)
                    
                    # Draw main gate label
                    painter.setBrush(QColor("#9B59B6"))
                    painter.setPen(QPen(QColor("#8E44AD"), 2))
                    painter.drawRoundedRect(x - 30, y - 25, 60, 50, 10, 10)
                    
                    painter.setPen(QColor("#FFFFFF"))
                    font = QFont("SF Pro Display", 10, QFont.Bold)
                    painter.setFont(font)
                    painter.drawText(x - 30, y - 25, 60, 25, Qt.AlignCenter, gate_type)
                    
                    # Draw parameters
                    font = QFont("SF Pro Display", 8)
                    painter.setFont(font)
                    painter.drawText(x - 30, y, 60, 25, Qt.AlignCenter, f"({base},{modulus})")
                    
                    # Draw control/target markers
                    for cq in control_qubits:
                        cy = 50 + cq * self.qubit_spacing
                        painter.setBrush(QColor("#4A90E2"))
                        painter.setPen(QPen(QColor("#667eea"), 2))
                        painter.drawEllipse(x - 6, cy - 6, 12, 12)
                    
                    for tq in target_qubits:
                        ty = 50 + tq * self.qubit_spacing
                        painter.setBrush(Qt.NoBrush)
                        painter.setPen(QPen(QColor("#9B59B6"), 2))
                        painter.drawRect(x - 6, ty - 6, 12, 12)
                    
                    continue
            
            # QFT/QFT_INV gate - Multi-qubit transform
            if gate_type in ['QFT', 'QFT_INV']:
                params = gate.get('params', {})
                qft_qubits = params.get('qubits', [qubit])
                is_inverse = params.get('is_inverse', gate_type == 'QFT_INV')
                
                if len(qft_qubits) > 1:
                    # Multi-qubit QFT
                    min_q = min(qft_qubits)
                    max_q = max(qft_qubits)
                    top_y = 50 + min_q * self.qubit_spacing
                    bottom_y = 50 + max_q * self.qubit_spacing
                    height = bottom_y - top_y + 40
                    
                    # Draw spanning box
                    qft_color = QColor("#27AE60") if not is_inverse else QColor("#E67E22")
                    painter.setBrush(QColor(qft_color.red(), qft_color.green(), qft_color.blue(), 40))
                    painter.setPen(QPen(qft_color, 3))
                    painter.drawRoundedRect(x - 35, top_y - 20, 70, height, 12, 12)
                    
                    # Draw QFT label
                    painter.setBrush(qft_color)
                    painter.setPen(QPen(qft_color.darker(120), 2))
                    center_y = (top_y + bottom_y) // 2
                    painter.drawRoundedRect(x - 30, center_y - 25, 60, 50, 10, 10)
                    
                    painter.setPen(QColor("#FFFFFF"))
                    font = QFont("SF Pro Display", 11, QFont.Bold)
                    painter.setFont(font)
                    label = "QFT†" if is_inverse else "QFT"
                    painter.drawText(x - 30, center_y - 25, 60, 50, Qt.AlignCenter, label)
                    
                    continue
            
            # ============================================================
            # Original V1.0 Gates
            # ============================================================
            
            # 如果是多量子比特门，先绘制控制线
            if control is not None and gate_type in ['CNOT', 'CZ', 'SWAP']:
                control_y = 50 + control * self.qubit_spacing
                
                # 绘制发光连接线
                gradient = QLinearGradient(x, control_y, x, y)
                gradient.setColorAt(0, QColor(74, 144, 226, 150))
                gradient.setColorAt(1, QColor(155, 89, 182, 150))
                
                painter.setPen(QPen(gradient, 4))
                painter.drawLine(x, control_y, x, y)
                
                # 绘制控制点（发光圆圈）
                painter.setBrush(QColor("#4A90E2"))
                painter.setPen(QPen(QColor("#667eea"), 2))
                painter.drawEllipse(x - 8, control_y - 8, 16, 16)
                
                # CNOT的目标点（⊕符号）
                if gate_type == 'CNOT':
                    # 外圈发光
                    painter.setBrush(Qt.NoBrush)
                    painter.setPen(QPen(QColor("#667eea"), 4))
                    painter.drawEllipse(x - 22, y - 22, 44, 44)
                    
                    # 内圈
                    painter.setPen(QPen(color, 3))
                    painter.drawEllipse(x - 18, y - 18, 36, 36)
                    
                    # ⊕符号
                    painter.drawLine(x - 12, y, x + 12, y)
                    painter.drawLine(x, y - 12, x, y + 12)
                    continue
                
                elif gate_type == 'SWAP':
                    # SWAP用X符号 - 发光效果
                    painter.setPen(QPen(color, 4))
                    painter.drawLine(x - 12, control_y - 12, x + 12, control_y + 12)
                    painter.drawLine(x - 12, control_y + 12, x + 12, control_y - 12)
                    painter.drawLine(x - 12, y - 12, x + 12, y + 12)
                    painter.drawLine(x - 12, y + 12, x + 12, y - 12)
                    continue
            
            # 绘制普通门框 - 带渐变和发光
            # 外层发光
            glow_color = QColor(color)
            glow_color.setAlpha(60)
            painter.setBrush(glow_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x - self.gate_width//2 - 3, y - 23,
                                  self.gate_width + 6, 46, 14, 14)
            
            # 主门框 - 渐变
            gradient = QLinearGradient(x, y - 20, x, y + 20)
            bright_color = QColor(color).lighter(120)
            gradient.setColorAt(0, bright_color)
            gradient.setColorAt(1, color)
            
            painter.setBrush(gradient)
            painter.setPen(QPen(color.darker(130), 2))
            painter.drawRoundedRect(x - self.gate_width//2, y - 20,
                                  self.gate_width, 40, 10, 10)
            
            # 绘制门标签 - 白色加粗
            painter.setPen(QColor("#FFFFFF"))
            font = QFont("SF Pro Display", 12, QFont.Bold)
            painter.setFont(font)
            painter.drawText(x - self.gate_width//2, y - 20,
                           self.gate_width, 40,
                           Qt.AlignCenter, gate_type)
