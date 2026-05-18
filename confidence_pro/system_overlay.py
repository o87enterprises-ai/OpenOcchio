#!/usr/bin/env python3
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal, Slot

# Keep the interpret_confidence function (or import from wrapper)
def interpret_confidence(conf):
    if conf >= 0.8:
        return "Confident", "\033[92m", "Confident"
    elif conf >= 0.6:
        return "Not so confident", "\033[93m", "Not so confident"
    elif conf >= 0.4:
        return "Unsure", "\033[33m", "Unsure"
    elif conf >= 0.2:
        return "Kind of insecure", "\033[31m", "Kind of insecure"
    else:
        return "Insecure", "\033[41m\033[37m", "Insecure"

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
        self.setGeometry(screen.width() - 250, screen.height() - 150, 220, 100)
        
        layout = QVBoxLayout()
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: white;
                border: 2px solid #eee;
                border-radius: 15px;
            }
            QLabel { color: #2c3e50; font-family: 'Arial'; }
            QProgressBar {
                border: 2px solid #eee;
                border-radius: 5px;
                text-align: center;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
        """)
        
        inner_layout = QVBoxLayout(self.container)
        self.header = QLabel("OpenOcchio Gauge")
        self.header.setStyleSheet("font-weight: bold; font-size: 12px; color: #7f8c8d;")
        inner_layout.addWidget(self.header)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        inner_layout.addWidget(self.progress)
        
        label_layout = QHBoxLayout()
        self.score_label = QLabel("0.00")
        self.score_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        label_layout.addWidget(self.score_label)
        
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 10px;")
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
        label, color_code, score_text = interpret_confidence(score)
        hex_color = "#2ecc71"
        if score < 0.8: hex_color = "#f1c40f"
        if score < 0.6: hex_color = "#e67e22"
        if score < 0.4: hex_color = "#e74c3c"
        
        self.progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {hex_color}; }}")
        self.progress.setValue(int(score * 100))
        self.score_label.setText(f"{score:.2f}")
        self.score_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {hex_color};")
        self.status_label.setText(score_text.upper())
        self.status_label.setStyleSheet(f"font-weight: bold; font-size: 10px; color: {hex_color};")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ConfidenceOverlay()
    sys.exit(app.exec())