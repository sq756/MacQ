"""
MacQ GUI - Theme Management and Styles
Supports dynamic switching between multiple premium themes.
"""

from PySide6.QtGui import QColor

class Theme:
    """Base class for themes"""
    def __init__(self, name, main_window, palette, circuit, visualizer, run_btn, clear_btn):
        self.name = name
        self.main_window = main_window
        self.palette = palette
        self.circuit = circuit
        self.visualizer = visualizer
        self.run_btn = run_btn
        self.clear_btn = clear_btn

# ============================================================================
# Theme 1: Quantum Dark (Default)
# ============================================================================
QUANTUM_DARK = Theme(
    name="Quantum Dark",
    main_window="""
        QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0A0E27, stop:1 #1A1E3F); }
        QWidget { color: #E8E8E8; font-family: '.AppleSystemUIFont', sans-serif; }
        QMenuBar { background: rgba(20, 24, 45, 0.85); border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        QMenu { background: rgba(30, 34, 55, 0.95); border: 1px solid rgba(255, 255, 255, 0.1); }
        QToolBar { background: rgba(20, 24, 45, 0.7); border: none; }
        QStatusBar { background: rgba(15, 19, 35, 0.9); color: #A0A0A0; }
        QSpinBox { background: rgba(40, 44, 65, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: #E8E8E8; }
    """,
    palette="""
        QWidget { background: rgba(20, 24, 45, 0.6); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); }
        QGroupBox { border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; background: rgba(30, 34, 55, 0.4); color: #B0B0B0; }
    """,
    circuit="""
        QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0F1323, stop:1 #191D32); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; }
    """,
    visualizer="""
        QWidget { background: rgba(20, 24, 45, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); }
    """,
    run_btn="""
        QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5B86E5, stop:1 #36D1DC); color: white; border: none; padding: 10px 24px; border-radius: 10px; font-weight: bold; }
        QPushButton:hover { background: #6B96F5; }
    """,
    clear_btn="""
        QPushButton { background: rgba(226, 74, 74, 0.8); color: white; border: none; padding: 10px 20px; border-radius: 10px; font-weight: 600; }
        QPushButton:hover { background: rgba(236, 84, 84, 0.9); }
    """
)

# ============================================================================
# Theme 2: Classic Academic (Light Mode)
# ============================================================================
CLASSIC_LIGHT = Theme(
    name="Classic Light",
    main_window="""
        QMainWindow { background: #F5F7FA; }
        QWidget { color: #2D3436; font-family: 'SF Pro Display', sans-serif; }
        QMenuBar { background: #FFFFFF; border-bottom: 1px solid #DCDDE1; }
        QMenu { background: #FFFFFF; border: 1px solid #DCDDE1; }
        QToolBar { background: #F0F2F5; border: none; }
        QStatusBar { background: #FFFFFF; color: #636E72; }
        QSpinBox { background: #FFFFFF; border: 1px solid #DCDDE1; border-radius: 8px; color: #2D3436; }
    """,
    palette="""
        QWidget { background: #FFFFFF; border-radius: 16px; border: 1px solid #DCDDE1; }
        QGroupBox { border: 1px solid #DCDDE1; border-radius: 12px; background: #F9FAFB; color: #636E72; }
    """,
    circuit="""
        QWidget { background: #FFFFFF; border: 1px solid #DCDDE1; border-radius: 16px; }
    """,
    visualizer="""
        QWidget { background: #FFFFFF; border-radius: 16px; border: 1px solid #DCDDE1; }
    """,
    run_btn="""
        QPushButton { background: #0984E3; color: white; border: none; padding: 10px 24px; border-radius: 10px; font-weight: bold; }
        QPushButton:hover { background: #74B9FF; }
    """,
    clear_btn="""
        QPushButton { background: #D63031; color: white; border: none; padding: 10px 20px; border-radius: 10px; font-weight: 600; }
        QPushButton:hover { background: #FF7675; }
    """
)

# ============================================================================
# Theme 3: Neon Future (High Contrast)
# ============================================================================
NEON_FUTURE = Theme(
    name="Neon Future",
    main_window="""
        QMainWindow { background: #000000; }
        QWidget { color: #00FF9F; font-family: 'Fira Code', monospace; }
        QMenuBar { background: #000000; border-bottom: 2px solid #00FF9F; }
        QMenu { background: #000000; border: 1px solid #00FF9F; }
        QToolBar { background: #111111; border: none; }
        QStatusBar { background: #000000; color: #00FF9F; }
        QSpinBox { background: #000000; border: 1px solid #00FF9F; border-radius: 0px; color: #00FF9F; }
    """,
    palette="""
        QWidget { background: #000000; border-radius: 0px; border: 1px solid #00FF9F; }
        QGroupBox { border: 1px solid #00FF9F; border-radius: 0px; background: #000000; color: #00FF9F; }
    """,
    circuit="""
        QWidget { background: #000000; border: 1px solid #00FF9F; border-radius: 0px; }
    """,
    visualizer="""
        QWidget { background: #000000; border-radius: 0px; border: 1px solid #00FF9F; }
    """,
    run_btn="""
        QPushButton { background: #00FF9F; color: black; border: none; padding: 10px 24px; border-radius: 0px; font-weight: bold; }
        QPushButton:hover { background: #FFFFFF; }
    """,
    clear_btn="""
        QPushButton { background: #FF0055; color: white; border: none; padding: 10px 20px; border-radius: 0px; font-weight: 600; }
        QPushButton:hover { background: #FF5599; }
    """
)

THEMES = {
    "Quantum Dark": QUANTUM_DARK,
    "Classic Light": CLASSIC_LIGHT,
    "Neon Future": NEON_FUTURE
}

# Compatibility for old code
MAIN_WINDOW_STYLE = QUANTUM_DARK.main_window
GATE_PALETTE_STYLE = QUANTUM_DARK.palette
CIRCUIT_EDITOR_STYLE = QUANTUM_DARK.circuit
VISUALIZER_STYLE = QUANTUM_DARK.visualizer
RUN_BUTTON_STYLE = QUANTUM_DARK.run_btn
CLEAR_BUTTON_STYLE = QUANTUM_DARK.clear_btn

GATE_COLORS = {
    'H': '#667eea', 'X': '#f093fb', 'Y': '#fa709a', 'Z': '#30cfd0',
    'I': '#a8a8a8', 'S': '#a044ff', 'T': '#ff6a88', 'Rx': '#00c6ff',
    'Ry': '#f77062', 'Rz': '#2af598', 'CNOT': '#8e2de2', 'CZ': '#06beb6',
    'SWAP': '#ffa751', 'Toffoli': '#fc4a1a', 'MEASURE': '#e74c3c',
    'QFT': '#27ae60', 'QFT_INV': '#e67e22', 'MOD_EXP': '#9b59b6'
}

# Premium gradients for buttons
GATE_COLORS_PREMIUM = {
    'H': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #667eea, stop:1 #764ba2)',
    'X': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f093fb, stop:1 #f5576c)',
    'Y': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fa709a, stop:1 #fee140)',
    'Z': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #30cfd0, stop:1 #330867)',
    'I': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a8a8a8, stop:1 #7a7a7a)',
    'S': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a044ff, stop:1 #6a3093)',
    'T': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6a88, stop:1 #ff4a6a)',
    'S†': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b044ff, stop:1 #7a40a3)',
    'T†': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff7a98, stop:1 #ff5a7a)',
    'Rx': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00c6ff, stop:1 #0072ff)',
    'Ry': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f77062, stop:1 #fe5196)',
    'Rz': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2af598, stop:1 #009efd)',
    'CNOT': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8e2de2, stop:1 #4a00e0)',
    'CZ': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #06beb6, stop:1 #48b1bf)',
    'SWAP': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffa751, stop:1 #ffe259)',
    'Toffoli': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fc4a1a, stop:1 #f7b733)',
    'MEASURE': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e74c3c, stop:1 #c0392b)',
    'QFT': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #27ae60, stop:1 #1e8449)',
    'QFT_INV': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e67e22, stop:1 #d35400)',
    'MOD_EXP': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9b59b6, stop:1 #8e44ad)'
}
