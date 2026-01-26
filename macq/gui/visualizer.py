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
    """概率分布图 - Premium版本"""
    
    def __init__(self):
        fig = Figure(figsize=(5, 4), dpi=100, facecolor='#FAFAFA')
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        
        # 初始样式
        self.axes.set_facecolor('#FFFFFF')
        self.axes.set_title('量子态概率分布', fontsize=14, fontweight='bold', color='#2C3E50')
        self.axes.set_xlabel('量子态', fontsize=11, color='#555')
        self.axes.set_ylabel('概率', fontsize=11, color='#555')
        self.axes.set_ylim([0, 1])
        self.axes.grid(True, alpha=0.2, linestyle='--')
        
        # 美化边框
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        
    def update_probabilities(self, state):
        """更新概率显示 - 智能优化版本"""
        probs = state.probabilities()
        num_qubits = state.num_qubits
        
        self.axes.clear()
        
        # 智能显示：只显示概率>阈值的基态
        threshold = 0.001  # 0.1%
        significant_indices = [i for i, p in enumerate(probs) if p > threshold]
        
        # 如果显著的基态少于10个，显示全部
        if len(significant_indices) == 0:
            significant_indices = list(range(min(10, len(probs))))
        elif len(significant_indices) > 20:
            # 太多的话，只显示Top 20
            sorted_indices = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
            significant_indices = sorted(sorted_indices[:20])
        
        # 提取显著概率
        sig_probs = [probs[i] for i in significant_indices]
        labels = [f"|{i:0{num_qubits}b}⟩" for i in significant_indices]
        
        # 创建渐变颜色
        colors = []
        for p in sig_probs:
            # 根据概率大小设置颜色：高概率=亮蓝色，低概率=暗蓝色
            intensity = 0.3 + 0.7 * (p / max(sig_probs)) if max(sig_probs) > 0 else 0.5
            colors.append((0.29 * intensity, 0.56 * intensity, 0.89 * intensity))
        
        # 绘制柱状图
        bars = self.axes.bar(range(len(sig_probs)), sig_probs, 
                            color=colors, 
                            edgecolor='white', 
                            linewidth=1.5,
                            alpha=0.9)
        
        # 高亮最高概率
        if sig_probs:
            max_idx = sig_probs.index(max(sig_probs))
            bars[max_idx].set_color('#FF6B9D')
            bars[max_idx].set_edgecolor('#FF1744')
            bars[max_idx].set_linewidth(2.5)
        
        # 设置标题和标签
        self.axes.set_title(
            f'{num_qubits}量子比特态概率分布',
            fontsize=14,
            fontweight='bold',
            color='#2C3E50',
            pad=15
        )
        
        self.axes.set_xlabel('量子态', fontsize=11, color='#555', fontweight='600')
        self.axes.set_ylabel('概率', fontsize=11, color='#555', fontweight='600')
        self.axes.set_ylim([0, min(1.1, max(sig_probs) * 1.2) if sig_probs else 1])
        
        # 设置x轴
        self.axes.set_xticks(range(len(sig_probs)))
        self.axes.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        
        # 美化网格
        self.axes.grid(True, axis='y', alpha=0.2, linestyle='--', linewidth=0.8)
        self.axes.set_axisbelow(True)
        
        # 移除顶部和右侧边框
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_color('#CCCCCC')
        self.axes.spines['bottom'].set_color('#CCCCCC')
        
        # 在柱子上显示概率值（只显示>5%的）
        for i, (bar, prob) in enumerate(zip(bars, sig_probs)):
            if prob > 0.05:  # 只标注大于5%的
                height = bar.get_height()
                self.axes.text(
                    bar.get_x() + bar.get_width()/2., 
                    height + 0.02,
                    f'{prob:.1%}',
                    ha='center', 
                    va='bottom',
                    fontsize=9,
                    fontweight='bold',
                    color='#FF6B9D' if i == max_idx else '#4A90E2'
                )
        
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
