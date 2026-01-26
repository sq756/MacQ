"""
MacQ GUI - Modern Premium Styles
Glassmorphism + Dark Mode + Gradients
"""

MAIN_WINDOW_STYLE = """
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0A0E27,
        stop:1 #1A1E3F
    );
}

QWidget {
    color: #E8E8E8;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue";
}

/* Menu Bar */
QMenuBar {
    background: rgba(20, 24, 45, 0.85);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 5px;
}

QMenuBar::item {
    background: transparent;
    padding: 8px 12px;
    border-radius: 6px;
    color: #E8E8E8;
}

QMenuBar::item:selected {
    background: rgba(74, 144, 226, 0.3);
}

QMenu {
    background: rgba(30, 34, 55, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px;
}

QMenu::item {
    padding: 8px 30px 8px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background: rgba(74, 144, 226, 0.4);
}

/* Tool Bar */
QToolBar {
    background: rgba(20, 24, 45, 0.7);
    border: none;
    padding: 10px;
    spacing: 10px;
}

/* Status Bar */
QStatusBar {
    background: rgba(15, 19, 35, 0.9);
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    color: #A0A0A0;
}

/* Splitter */
QSplitter::handle {
    background: rgba(255, 255, 255, 0.05);
    width: 2px;
}

QSplitter::handle:hover {
    background: rgba(74, 144, 226, 0.5);
}

/* Spin Box */
QSpinBox {
    background: rgba(40, 44, 65, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 6px 12px;
    color: #E8E8E8;
    min-width: 60px;
}

QSpinBox:hover {
    border: 1px solid rgba(74, 144, 226, 0.5);
    background: rgba(40, 44, 65, 0.8);
}

QSpinBox::up-button, QSpinBox::down-button {
    background: rgba(74, 144, 226, 0.2);
    border: none;
    border-radius: 4px;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: rgba(74, 144, 226, 0.4);
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    background: rgba(20, 24, 45, 0.4);
}

QTabBar::tab {
    background: rgba(40, 44, 65, 0.4);
    color: #A0A0A0;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: rgba(74, 144, 226, 0.3);
    color: #FFFFFF;
    border-bottom: 3px solid #4A90E2;
}

QTabBar::tab:hover:!selected {
    background: rgba(74, 144, 226, 0.15);
}

/* Labels */
QLabel {
    color: #E8E8E8;
}
"""

GATE_PALETTE_STYLE = """
QWidget {
    background: rgba(20, 24, 45, 0.6);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

QPushButton {
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-weight: 600;
    font-size: 14px;
    color: white;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(74, 144, 226, 0.8),
        stop:1 rgba(74, 144, 226, 0.6)
    );
}

QPushButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(84, 154, 236, 0.9),
        stop:1 rgba(84, 154, 236, 0.7)
    );
}

QPushButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(64, 134, 216, 0.9),
        stop:1 rgba(64, 134, 216, 0.7)
    );
}

QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 18px;
    background: rgba(30, 34, 55, 0.4);
    font-weight: 600;
    color: #B0B0B0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 4px 12px;
    background: rgba(74, 144, 226, 0.2);
    border-radius: 6px;
    color: #E8E8E8;
}
"""

CIRCUIT_EDITOR_STYLE = """
QWidget {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(15, 19, 35, 0.4),
        stop:1 rgba(25, 29, 50, 0.4)
    );
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
}
"""

VISUALIZER_STYLE = """
QWidget {
    background: rgba(20, 24, 45, 0.5);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
"""

RUN_BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #5B86E5,
        stop:1 #36D1DC
    );
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 14px;
    min-width: 100px;
}

QPushButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6B96F5,
        stop:1 #46E1EC
    );
}

QPushButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #4B76D5,
        stop:1 #26C1CC
    );
}
"""

CLEAR_BUTTON_STYLE = """
QPushButton {
    background: rgba(226, 74, 74, 0.8);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    font-weight: 600;
}

QPushButton:hover {
    background: rgba(236, 84, 84, 0.9);
}

QPushButton:pressed {
    background: rgba(216, 64, 64, 0.9);
}
"""

# Gate colors with gradients
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
    'Toffoli': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fc4a1a, stop:1 #f7b733)'
}
