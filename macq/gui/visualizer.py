"""
MacQ GUI - Visualization Widget
Probability charts and state visualization
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use('Qt5Agg')
# 配置中文字体
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']  # macOS中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np


class VisualizationWidget(QWidget):
    """可视化面板"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(300)
        self._init_ui()
        self.current_state = None
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title = QLabel("量子态可视化")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(title)
        
        # 标签页
        self.tabs = QTabWidget()
        
        # 概率分布图
        self.prob_chart = ProbabilityChart()
        self.tabs.addTab(self.prob_chart, "📊 概率分布")
        
        # 态向量视图
        self.state_view = StateVectorView()
        self.tabs.addTab(self.state_view, "🔢 态向量")
        
        layout.addWidget(self.tabs)
        
    def update_state(self, quantum_state):
        """更新量子态显示"""
        self.current_state = quantum_state
        
        # 更新概率图
        self.prob_chart.update_probabilities(quantum_state)
        
        # 更新态向量
        self.state_view.update_state(quantum_state)
    
    def clear(self):
        """清空显示"""
        self.current_state = None
        self.prob_chart.clear()
        self.state_view.clear()


class ProbabilityChart(FigureCanvasQTAgg):
    """概率分布图"""
    
    def __init__(self):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        
        self.axes.set_title('基态概率分布')
        self.axes.set_xlabel('基态')
        self.axes.set_ylabel('概率')
        self.axes.set_ylim([0, 1])
        self.axes.grid(True, alpha=0.3)
        
    def update_probabilities(self, state):
        """更新概率显示"""
        probs = state.probabilities()
        num_qubits = state.num_qubits
        
        # 生成标签
        if num_qubits <= 4:
            # 少量量子比特：显示所有基态
            labels = [f"|{i:0{num_qubits}b}⟩" for i in range(len(probs))]
        else:
            # 多量子比特：只显示索引
            labels = [str(i) for i in range(len(probs))]
        
        self.axes.clear()
        
        # 绘制柱状图
        bars = self.axes.bar(range(len(probs)), probs, color='#4A90E2', alpha=0.7)
        
        # 高亮非零概率
        for i, (bar, prob) in enumerate(zip(bars, probs)):
            if prob > 0.01:  # 超过1%
                bar.set_color('#E24A4A')
                bar.set_alpha(0.9)
        
        self.axes.set_title(f'{num_qubits}量子比特态概率分布')
        self.axes.set_xlabel('基态')
        self.axes.set_ylabel('概率')
        self.axes.set_ylim([0, 1.1])
        
        # 设置x轴标签
        if num_qubits <= 4:
            self.axes.set_xticks(range(len(probs)))
            self.axes.set_xticklabels(labels, rotation=45, ha='right')
        else:
            # 太多标签时，只显示部分
            step = max(1, len(probs) // 10)
            self.axes.set_xticks(range(0, len(probs), step))
            self.axes.set_xticklabels([labels[i] for i in range(0, len(probs), step)])
        
        self.axes.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.draw()
    
    def clear(self):
        """清空图表"""
        self.axes.clear()
        self.axes.set_title('基态概率分布')
        self.axes.set_xlabel('基态')
        self.axes.set_ylabel('概率')
        self.axes.set_ylim([0, 1])
        self.axes.grid(True, alpha=0.3)
        self.draw()


class StateVectorView(QWidget):
    """态向量视图"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.label = QLabel("运行电路后将显示态向量")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 20px;
            }
        """)
        
        layout.addWidget(self.label)
        
    def update_state(self, state):
        """更新态向量显示"""
        vec = state.get_statevector()
        num_qubits = state.num_qubits
        
        # 构建显示文本
        text = f"<h3>{num_qubits}量子比特态向量</h3>"
        text += "<table style='font-family: monospace;'>"
        text += "<tr><th>基态</th><th>振幅</th><th>概率</th></tr>"
        
        # 只显示非零或前10个
        count = 0
        for i, amp in enumerate(vec):
            prob = abs(amp) ** 2
            if prob > 1e-6 or (count < 10 and i < len(vec)):
                basis = f"|{i:0{num_qubits}b}⟩"
                amp_str = f"{amp.real:.4f}{amp.imag:+.4f}i"
                prob_str = f"{prob:.4f}"
                
                text += f"<tr><td>{basis}</td><td>{amp_str}</td><td>{prob_str}</td></tr>"
                count += 1
                
                if count >= 10:
                    break
        
        if len(vec) > count:
            text += f"<tr><td colspan='3'>... 还有 {len(vec) - count} 项</td></tr>"
        
        text += "</table>"
        
        self.label.setText(text)
    
    def clear(self):
        """清空显示"""
        self.label.setText("运行电路后将显示态向量")
