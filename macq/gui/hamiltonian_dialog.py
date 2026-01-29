"""
MacQ GUI - Hamiltonian Matrix Dialog
Visualizes the unitary matrix (Hamiltonian-related) of the quantum circuit.
"""

import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QFrame, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont, QBrush, QLinearGradient

class HamiltonianDialog(QDialog):
    """哈密顿量/幺正矩阵可视化对话框 - Premium Design"""
    
    def __init__(self, matrix, parent=None):
        super().__init__(parent)
        self.matrix = matrix
        self.size = matrix.shape[0]
        self.num_qubits = int(np.log2(self.size))
        
        self.setWindowTitle("Circuit Hamiltonian / Unitary Matrix")
        self.resize(900, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #0F111A;
                color: #B0B0B0;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'SF Pro Display';
            }
            QTableWidget {
                background-color: #1A1D2B;
                gridline-color: #2D324A;
                border: 1px solid #2D324A;
                border-radius: 8px;
                color: #E0E0E0;
                font-family: 'Fira Code', 'Courier New';
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #24283B;
                color: #4A90E2;
                padding: 6px;
                border: 1px solid #2D324A;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #2D324A;
                background: #1A1D2B;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #1A1D2B;
                color: #808080;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #24283B;
                color: #4A90E2;
                border-bottom: 2px solid #4A90E2;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #667eea);
                border: none;
                color: white;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5B96E5, stop:1 #788AFA);
            }
        """)
        
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Title and Info
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Matrix Representation ({self.num_qubits} Qubits)")
        title_label.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        header_layout.addWidget(title_label)
        
        stats_label = QLabel(f"Size: {self.size} x {self.size}")
        stats_label.setStyleSheet("color: #808080; font-size: 14px;")
        header_layout.addStretch()
        header_layout.addWidget(stats_label)
        layout.addLayout(header_layout)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # 1. Numerical View
        self.table = QTableWidget(self.size, self.size)
        self._populate_table()
        self.tabs.addTab(self.table, "数值视图 (Numerical)")
        
        # 2. Magnitude Heatmap (Placeholder for now, can be improved with custom painting)
        self.heatmap_label = QLabel("Heatmap visualization coming soon for larger circuits...")
        self.heatmap_label.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(self.heatmap_label, "热力图 (Heatmap)")
        
        layout.addWidget(self.tabs)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Done")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def _populate_table(self):
        # Set headers
        headers = [f"|{bin(i)[2:].zfill(self.num_qubits)}⟩" for i in range(self.size)]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setVerticalHeaderLabels(headers)
        
        # Color scale for background
        for r in range(self.size):
            for c in range(self.size):
                val = self.matrix[r, c]
                mag = np.abs(val)
                phase = np.angle(val)
                
                # Format string: real + imag j
                real_str = f"{val.real:.3f}".rstrip('0').rstrip('.')
                imag_str = f"{val.imag:+.3f}j".rstrip('0').rstrip('.')
                if imag_str == "+j": imag_str = "+1j"
                if imag_str == "-j": imag_str = "-1j"
                if abs(val.imag) < 1e-6:
                    text = real_str if real_str else "0"
                elif abs(val.real) < 1e-6:
                    text = imag_str
                else:
                    text = f"{real_str}{imag_str}"
                
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                
                # Set background based on magnitude
                alpha = int(mag * 100) # Max 100 alpha for visibility
                if alpha > 0:
                    bg_color = QColor(74, 144, 226, alpha)
                    item.setBackground(QBrush(bg_color))
                
                # Set text color
                if mag > 0.5:
                    item.setForeground(QBrush(QColor("#FFFFFF")))
                else:
                    item.setForeground(QBrush(QColor("#B0B0B0")))
                
                self.table.setItem(r, c, item)
        
        # Adjust column widths
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        if self.size < 8:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
