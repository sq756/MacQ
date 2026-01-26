"""
MacQ GUI - Gate Palette Widget
Quantum gate selection panel with drag-and-drop support
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QGroupBox, QToolTip
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag, QCursor


class GatePaletteWidget(QWidget):
    """量子门选择面板"""
    
    gate_selected = Signal(str)  # 当门被选中时发出信号
    
    # 门分类
    GATE_CATEGORIES = {
        "基础门": ["H", "X", "Y", "Z", "I"],
        "相位门": ["S", "T", "S†", "T†"],
        "旋转门": ["Rx", "Ry", "Rz"],
        "双比特门": ["CNOT", "CZ", "SWAP"],
        "多比特门": ["Toffoli"]
    }
    
    # 门的颜色
    GATE_COLORS = {
        'H': '#4A90E2',    # 蓝色
        'X': '#E24A4A',    # 红色
        'Y': '#E2A44A',    # 橙色
        'Z': '#4AE2A4',    # 绿色
        'S': '#9B59B6',    # 紫色
        'T': '#E74C3C',    # 深红
        'CNOT': '#8E44AD', # 深紫
        'CZ': '#16A085',   # 青色
        'SWAP': '#F39C12', # 金色
        'Toffoli': '#C0392B' # 褐红
    }
    
    # 门的说明
    GATE_DESCRIPTIONS = {
        'H': 'Hadamard门 - 创建叠加态',
        'X': 'Pauli-X门 - 量子NOT门',
        'Y': 'Pauli-Y门 - Y轴旋转',
        'Z': 'Pauli-Z门 - 相位翻转',
        'I': '单位门 - 不做任何操作',
        'S': 'S门 - π/2相位门',
        'T': 'T门 - π/4相位门',
        'S†': 'S†门 - S门的逆',
        'T†': 'T†门 - T门的逆',
        'Rx': 'Rx门 - 绕X轴旋转',
        'Ry': 'Ry门 - 绕Y轴旋转',
        'Rz': 'Rz门 - 绕Z轴旋转',
        'CNOT': 'CNOT门 - 受控非门',
        'CZ': 'CZ门 - 受控Z门',
        'SWAP': 'SWAP门 - 交换两个量子比特',
        'Toffoli': 'Toffoli门 - 双控制非门'
    }
    
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(180)
        self.setMaximumWidth(250)
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title = QLabel("量子门")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(title)
        
        # 为每个类别创建分组
        for category, gates in self.GATE_CATEGORIES.items():
            group = self._create_gate_group(category, gates)
            layout.addWidget(group)
        
        layout.addStretch()
        
        # 说明文本
        info_label = QLabel("💡 拖拽门到电路编辑器")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 10px;
                background-color: #F0F0F0;
                border-radius: 4px;
            }
        """)
        layout.addWidget(info_label)
        
    def _create_gate_group(self, category, gates):
        """创建门分组"""
        group = QGroupBox(category)
        group_layout = QVBoxLayout()
        group_layout.setSpacing(5)
        
        for gate in gates:
            gate_btn = self._create_gate_button(gate)
            group_layout.addWidget(gate_btn)
        
        group.setLayout(group_layout)
        return group
    
    def _create_gate_button(self, gate_type):
        """创建单个门按钮"""
        btn = QPushButton(gate_type)
        btn.setMinimumHeight(35)
        
        # 获取颜色
        color = self.GATE_COLORS.get(gate_type, '#95A5A6')
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.3)};
            }}
        """)
        
        # 设置工具提示
        description = self.GATE_DESCRIPTIONS.get(gate_type, "量子门")
        btn.setToolTip(description)
        
        # 连接信号
        btn.clicked.connect(lambda: self.gate_selected.emit(gate_type))
        
        # 启用拖拽
        btn.setAcceptDrops(False)
        btn.mousePressEvent = lambda event, g=gate_type: self._start_drag(event, g)
        
        return btn
    
    def _start_drag(self, event, gate_type):
        """开始拖拽操作"""
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(gate_type)
            drag.setMimeData(mime_data)
            
            # 设置拖拽光标
            drag.exec_(Qt.CopyAction)
    
    def _darken_color(self, hex_color, factor=0.2):
        """使颜色变暗"""
        # 简单实现：将RGB值乘以factor
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'
