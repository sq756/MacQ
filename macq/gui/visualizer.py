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
        
        # 概率分布图 (Histogram 2.0)
        self.prob_chart = ProbabilityChart()
        self.tabs.addTab(self.prob_chart, "📊 统计直方图")
        
        # 密度矩阵热力图
        self.heatmap_view = HeatmapView()
        self.tabs.addTab(self.heatmap_view, "🌡️ 密度矩阵")
        
        # 相位盘
        self.phase_disks = PhaseDiskView()
        self.tabs.addTab(self.phase_disks, "🧭 相位盘")
        
        # 态向量视图
        self.state_view = StateVectorView()
        self.tabs.addTab(self.state_view, "🔢 态向量")
        
        layout.addWidget(self.tabs)
        
    def update_state(self, quantum_state, density_matrix=None, counts=None, shots=None):
        """更新量子态显示"""
        self.current_state = quantum_state
        
        # 更新概率图 (Histogram 2.0)
        self.prob_chart.update_data(quantum_state, counts, shots)
        
        # 更新热力图
        if density_matrix:
            self.heatmap_view.update_heatmap(density_matrix)
        elif quantum_state:
            # 如果没有显式传DM，可以从QS生成（小规模比特）
            if quantum_state.num_qubits <= 6:
                from ..c_bridge import DensityMatrix
                dm = DensityMatrix.from_statevector(quantum_state)
                self.heatmap_view.update_heatmap(dm)
        
        # 更新相位盘
        self.phase_disks.update_disks(quantum_state)
        
        # 更新态向量
        self.state_view.update_state(quantum_state)
    
    def clear(self):
        """清空显示"""
        self.current_state = None
        self.prob_chart.clear()
        self.heatmap_view.clear()
        self.phase_disks.clear()
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
        
        # Register mapping: {reg_name: [qubit_indices]}
        self.registers = {}
        
    def update_data(self, state, counts=None, shots=None):
        """更新概率显示 - Histogram 2.0 (理论 vs 实验)"""
        theo_probs = state.probabilities()
        num_qubits = state.num_qubits
        
        self.axes.clear()
        
        # 智能选择显示的前 N 个基态
        threshold = 0.001
        significant_indices = [i for i, p in enumerate(theo_probs) if p > threshold]
        
        if counts:
            # 如果有采样数据，也包含采样中出现的索引
            for bin_str, _ in counts.items():
                idx = int(bin_str, 2)
                if idx not in significant_indices:
                    significant_indices.append(idx)
        
        significant_indices = sorted(significant_indices)
        if len(significant_indices) > 24:
            significant_indices = significant_indices[:24]
            
        def get_label(idx):
            bin_str = f"{idx:0{num_qubits}b}"
            if not self.registers:
                return f"|{bin_str}⟩"
            
            labels = []
            for name, indices in self.registers.items():
                val = 0
                for i, q_idx in enumerate(reversed(indices)):
                    if bin_str[q_idx] == '1':
                        val += (1 << i)
                labels.append(f"{name}={val}")
            return "| " + " ⊗ ".join(labels) + " ⟩"

        labels = [get_label(i) for i in significant_indices]
        theo_vals = [theo_probs[i] for i in significant_indices]
        
        x = np.arange(len(labels))
        width = 0.35 if counts else 0.7
        
        # 绘制理论值 (空心/浅色)
        self.axes.bar(x - (width/2 if counts else 0), theo_vals, width, 
                     label='理论值', color='#4A90E2', alpha=0.3, edgecolor='#4A90E2', hatch='//')
        
        # 绘制实验值 (实心)
        if counts and shots:
            exp_vals = [counts.get(l, 0) / shots for l in labels]
            error = [np.sqrt(v * (1-v) / shots) if shots > 0 else 0 for v in exp_vals]
            
            self.axes.bar(x + width/2, exp_vals, width, label='实验值', color='#FF6B9D', alpha=0.9)
            self.axes.errorbar(x + width/2, exp_vals, yerr=error, fmt='none', ecolor='#2C3E50', capsize=3)
            self.axes.legend()

        # 美化
        self.axes.set_title(f'量子态统计 (Shots={shots if shots else "∞"})', fontsize=14, fontweight='bold')
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        self.axes.set_ylim([0, max(max(theo_vals), max([counts.get(l, 0)/shots for l in labels] if counts else [0])) * 1.3 or 1.0])
        self.axes.grid(True, axis='y', alpha=0.2)
        
        self.figure.tight_layout()
        self.draw()
    
    def clear(self):
        """清空图表"""
        self.axes.clear()
        self.axes.set_title('量子态统计分布')
        self.draw()


class HeatmapView(FigureCanvasQTAgg):
    """密度矩阵热力图"""
    
    def __init__(self):
        fig = Figure(figsize=(6, 4), dpi=100)
        self.ax_real = fig.add_subplot(121)
        self.ax_imag = fig.add_subplot(122)
        super().__init__(fig)
        
    def update_heatmap(self, dm):
        data = dm.to_numpy()
        
        self.ax_real.clear()
        self.ax_imag.clear()
        
        im1 = self.ax_real.imshow(np.real(data), cmap='RdBu', vmin=-1, vmax=1)
        self.ax_real.set_title("实部 (Real)")
        
        im2 = self.ax_imag.imshow(np.imag(data), cmap='RdBu', vmin=-1, vmax=1)
        self.ax_imag.set_title("虚部 (Imag)")
        
        # 简单显示基态标签
        if dm.num_qubits <= 3:
            ticks = range(2**dm.num_qubits)
            labels = [f"{i:0{dm.num_qubits}b}" for i in ticks]
            self.ax_real.set_xticks(ticks)
            self.ax_real.set_xticklabels(labels, fontsize=8, rotation=90)
            self.ax_real.set_yticks(ticks)
            self.ax_real.set_yticklabels(labels, fontsize=8)
            
        self.figure.tight_layout()
        self.draw()
        
    def clear(self):
        self.ax_real.clear()
        self.ax_imag.clear()
        self.draw()


class PhaseDiskView(FigureCanvasQTAgg):
    """相位盘可视化"""
    
    def __init__(self):
        # 创建多个子图以容纳所有比特
        fig = Figure(figsize=(8, 3), dpi=100)
        super().__init__(fig)
        
    def update_disks(self, state):
        self.figure.clear()
        n = state.num_qubits
        display_n = min(n, 8)
        
        for i in range(display_n):
            ax = self.figure.add_subplot(1, display_n, i+1, projection='polar')
            
            # 简化版单比特相位：通过测量概率和相对相位估计
            # 在 MacQ 中，我们可以直接从状态向量提取
            # 对于比特 i，我们看 |...0...i...0...> vs |...0...1...0...> 这种基态的一个切片
            # 或者更准确地，计算约化密度矩阵 rho_i 的非对角项
            try:
                from ..c_bridge import DensityMatrix
                dm = DensityMatrix.from_statevector(state)
                # Trace out all but qubit i
                qubits_to_trace = [j for j in range(n) if j != i]
                rho_i = dm.partial_trace(qubits_to_trace).to_numpy()
                
                # rho_i = [[rho00, rho01], [rho10, rho11]]
                # rho11 是处于 |1> 的概率
                prob1 = np.real(rho_i[1, 1])
                # rho01 = <0|rho|1> = r * exp(-i*phi)
                # 相位 phi = arg(rho01)
                rho01 = rho_i[0, 1]
                phase = -np.angle(rho01) if abs(rho01) > 1e-6 else 0
                
                radius = np.sqrt(prob1)
                
                # 绘制相位指针
                ax.annotate("", xy=(phase, radius), xytext=(0, 0),
                            arrowprops=dict(arrowstyle="->", color='#4A90E2', lw=3))
                
                # 绘制圆盘背景 (代表概率幅)
                circle = plt.Circle((0, 0), 1.0, transform=ax.transData._b, color='#4A90E2', alpha=0.1)
                ax.add_artist(circle)
                
            except Exception as e:
                print(f"Phase disk error for q{i}: {e}")
            
            ax.set_ylim(0, 1)
            ax.set_title(f"q{i}", fontsize=11, fontweight='bold', color='#2C3E50')
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            ax.grid(True, alpha=0.1)
            
        self.figure.tight_layout()
        self.draw()
        
    def clear(self):
        self.figure.clear()
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
