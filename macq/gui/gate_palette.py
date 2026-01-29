from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QGroupBox, QToolTip, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag, QCursor, QColor

from .styles import GATE_PALETTE_STYLE, GATE_COLORS_PREMIUM


class GatePaletteWidget(QWidget):
    """量子门选择面板 - Premium Design"""
    
    gate_selected = Signal(str)
    
    # ... (保持原有的GATE_CATEGORIES和GATE_DESCRIPTIONS不变)
    
    # 门分类
        "多比特门": ["Toffoli"],
        "高级算法": ["QFT", "Grover", "Oracle"]
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
        'Toffoli': '#C0392B', # 褐红
        'QFT': '#FF4B2B',   # 红色渐变
        'Grover': '#1A2A6C', # 深蓝
        'Oracle': '#834D9B'  # 紫色
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
        'Toffoli': 'Toffoli门 - 双控制非门',
        'QFT': '量子傅里叶变换 - 变换基底',
        'Grover': 'Grover算子 - 扩散算子',
        'Oracle': '逻辑表达式生成器 - 点击配置'
    }
    
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(260)
        
        # 应用Premium样式
        self.setStyleSheet(GATE_PALETTE_STYLE)
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题（固定在顶部）
        title = QLabel("⚛️ Quantum Gates")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                color: #FFFFFF;
                background: rgba(30, 34, 55, 0.5);
            }
        """)
        main_layout.addWidget(title)
        
        # 可滚动区域
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(74, 144, 226, 0.5);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(74, 144, 226, 0.7);
            }
        """)
        
        # 滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(15, 10, 15, 10)
        scroll_layout.setSpacing(12)
        
        # 为每个类别创建分组（添加到滚动区域）
        for category, gates in self.GATE_CATEGORIES.items():
            group = self._create_gate_group(category, gates)
            scroll_layout.addWidget(group)
        
        # 底部间距
        scroll_layout.addStretch()
        
        # 说明文本
        info_label = QLabel("💡 拖拽门到电路\n或右键电路添加")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 11px;
                padding: 8px;
                background: rgba(74, 144, 226, 0.1);
                border-radius: 6px;
            }
        """)
        scroll_layout.addWidget(info_label)
        
        # 设置滚动区域
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
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
        """创建单个门按钮 - Premium版本"""
        btn = QPushButton(gate_type)
        btn.setMinimumHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        
        # 使用渐变背景
        gradient = GATE_COLORS_PREMIUM.get(
            gate_type,
            'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #95a5a6, stop:1 #7f8c8d)'
        )
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {gradient};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {gradient};
            }}
            QPushButton:pressed {{
                background: {gradient};
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 3)
        btn.setGraphicsEffect(shadow)
        
        # 设置工具提示
        description = self.GATE_DESCRIPTIONS.get(gate_type, "Quantum Gate")
        btn.setToolTip(description)
        
        # 连接信号
        btn.clicked.connect(lambda: self.gate_selected.emit(gate_type))
        
        # 启用拖拽
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
