#!/usr/bin/env python3
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, Slot, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient

# Design Tokens from Spec
TRUTH_GREEN = "#2ECC71"
UNCERTAIN_YELLOW = "#F1C40F"
LIE_RED = "#E74C3C"
WOOD_BASE = "#C49A6C"
OUTLINE_DARK = "#3A2F1F"

def interpret_confidence(conf):
    if conf >= 0.8:
        return "Truth", TRUTH_GREEN
    elif conf >= 0.4:
        return "Unsure", UNCERTAIN_YELLOW
    else:
        return "Lie", LIE_RED

class NoseGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.confidence = 1.0
        self.setMinimumHeight(80)
        self.setMinimumWidth(180)

    def setConfidence(self, value):
        self.confidence = max(0.0, min(1.0, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = 50 # Head center X
        cy = h // 2
        head_radius = 40

        # 1. Draw Head (Wood Texture)
        head_grad = QRadialGradient(cx - 10, cy - 10, head_radius + 20)
        head_grad.setColorAt(0, QColor("#e6ccb2")) # wood-light
        head_grad.setColorAt(0.6, QColor("#d2a679")) # wood-base
        head_grad.setColorAt(1, QColor("#8b5a2b")) # wood-dark
        
        painter.setBrush(head_grad)
        painter.setPen(QPen(QColor(OUTLINE_DARK), 3))
        painter.drawEllipse(cx - head_radius, cy - head_radius, head_radius * 2, head_radius * 2)

        # 2. Draw Eyes
        painter.setBrush(QColor("#1d1d1f"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 15, cy - 10, 8, 8)
        painter.drawEllipse(cx + 7, cy - 10, 8, 8)

        # 3. Draw Nose
        inverse_conf = 1.0 - self.confidence
        nose_length = 24 + (inverse_conf * 110)
        
        state_label, color_hex = interpret_confidence(self.confidence)
        color = QColor(color_hex)

        nose_grad = QRadialGradient(cx, cy, nose_length)
        nose_grad.setColorAt(0, QColor("#d2a679"))
        nose_grad.setColorAt(1, QColor("#8b5a2b"))

        painter.setBrush(nose_grad)
        painter.setPen(QPen(QColor(OUTLINE_DARK), 2))
        painter.drawRoundedRect(cx, cy - 7, nose_length, 14, 7, 7)

        # 4. Draw LED Tip
        led_radius = 7
        tip_x = cx + nose_length
        
        # Glow
        glow_alpha = int(120 + (inverse_conf * 135))
        glow_color = QColor(color)
        glow_color.setAlpha(glow_alpha)
        
        radial_grad = QRadialGradient(tip_x, cy, led_radius + 8)
        radial_grad.setColorAt(0, glow_color)
        radial_grad.setColorAt(1, QColor(0,0,0,0))
        
        painter.setBrush(radial_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(tip_x - led_radius - 8, cy - led_radius - 8, (led_radius + 8) * 2, (led_radius + 8) * 2)
        
        # Inner LED
        painter.setBrush(color)
        painter.setPen(QPen(QColor(0,0,0,60), 1))
        painter.drawEllipse(tip_x - led_radius, cy - led_radius, led_radius * 2, led_radius * 2)

class ConfidenceHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        conf = data.get('confidence', 0.5)
        self.server.overlay.update_signal.emit(conf)
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass

class ConfidenceOverlay(QWidget):
    update_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.update_signal.connect(self.update_gauge)
        
        # Start HTTP server to receive confidence from proxy
        self.server = HTTPServer(('localhost', 9876), ConfidenceHTTPHandler)
        self.server.overlay = self
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        # Adjusted size for the new head widget
        self.setGeometry(screen.width() - 250, screen.height() - 180, 230, 140)
        
        layout = QVBoxLayout()
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet(f"""
            #container {{
                background-color: white;
                border: 2px solid {OUTLINE_DARK};
                border-radius: 15px;
            }}
            QLabel {{ color: #2c3e50; font-family: 'Arial'; }}
        """)
        
        inner_layout = QVBoxLayout(self.container)
        self.header = QLabel("OpenOcchio Truth Meter")
        self.header.setStyleSheet("font-weight: bold; font-size: 11px; color: #7f8c8d;")
        inner_layout.addWidget(self.header)
        
        self.nose_gauge = NoseGauge()
        inner_layout.addWidget(self.nose_gauge)
        
        label_layout = QHBoxLayout()
        self.score_label = QLabel("1.00")
        self.score_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {TRUTH_GREEN};")
        label_layout.addWidget(self.score_label)
        
        self.status_label = QLabel("TRUTH")
        self.status_label.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {TRUTH_GREEN};")
        label_layout.addWidget(self.status_label)
        
        inner_layout.addLayout(label_layout)
        layout.addWidget(self.container)
        self.setLayout(layout)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    @Slot(float)
    def update_gauge(self, score):
        label, color_hex = interpret_confidence(score)
        
        self.nose_gauge.setConfidence(score)
        self.score_label.setText(f"{score:.2f}")
        self.score_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color_hex};")
        self.status_label.setText(label.upper())
        self.status_label.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {color_hex};")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ConfidenceOverlay()
    sys.exit(app.exec())
