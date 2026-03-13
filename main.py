import sys
import mss
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMenu
)
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import (
    QImage, QPixmap, QAction, QPainter, QPolygon, 
    QColor, QPen, QBrush, QCursor, QActionGroup, QIcon
)

def create_color_icon(color_name):
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color_name))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 12, 12, 4, 4)
    painter.end()
    return QIcon(pixmap)

def create_arrow_icon(direction, color_name="#9b59b6"):
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    painter.setBrush(QColor(color_name))
    painter.setPen(Qt.PenStyle.NoPen)
    
    pts = []
    if direction == "Top Left":
        pts = [QPoint(2, 2), QPoint(10, 2), QPoint(2, 10)]
    elif direction == "Top Right":
        pts = [QPoint(14, 2), QPoint(6, 2), QPoint(14, 10)]
    elif direction == "Bottom Left":
        pts = [QPoint(2, 14), QPoint(10, 14), QPoint(2, 6)]
    elif direction == "Bottom Right":
        pts = [QPoint(14, 14), QPoint(6, 14), QPoint(14, 6)]
    elif direction == "Top":
        pts = [QPoint(8, 2), QPoint(4, 8), QPoint(12, 8)]
    elif direction == "Bottom":
        pts = [QPoint(8, 14), QPoint(4, 8), QPoint(12, 8)]
    elif direction == "Left":
        pts = [QPoint(2, 8), QPoint(8, 4), QPoint(8, 12)]
    elif direction == "Right":
        pts = [QPoint(14, 8), QPoint(8, 4), QPoint(8, 12)]
    else: # None
        painter.setPen(QPen(QColor(color_name), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(4, 4, 8, 8)
        painter.end()
        return QIcon(pixmap)
        
    painter.drawPolygon(QPolygon(pts))
    painter.end()
    return QIcon(pixmap)

def create_app_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Background (Main Monitor)
    painter.setBrush(QColor("#2c3e50"))
    painter.setPen(QPen(QColor("#34495e"), 2))
    painter.drawRoundedRect(4, 16, 40, 32, 4, 4)
    
    # Foreground (Peek Monitor)
    painter.setBrush(QColor("#3498db"))
    painter.setPen(QPen(QColor("#2980b9"), 2))
    painter.drawRoundedRect(28, 8, 32, 24, 4, 4)
    
    # Eye/Peek symbol
    painter.setBrush(QColor("white"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(40, 16, 8, 8)
    painter.setBrush(QColor("#2c3e50"))
    painter.drawEllipse(42, 18, 4, 4)
    
    painter.end()
    return QIcon(pixmap)

class ViewerWindow(QMainWindow):
    def __init__(self, monitors, selected_indices, layout_type):
        super().__init__()
        self.setWindowTitle("OmniPeek")
        self.setWindowIcon(create_app_icon())
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        self.sct = mss.mss()
        self.monitors = monitors
        self.selected_indices = selected_indices
        self.layout_type = layout_type
        
        self.labels = []
        self.is_borderless = False
        self.snap_edge = "None"
        
        # Timer to debounce resize events and prevent "fighting" the OS
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.apply_aspect_ratio)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = None
        
        self.rebuild_layout()
        
        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Timer for screen capture
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(33) # ~30 FPS
        
    def rebuild_layout(self):
        if self.main_layout is not None:
            QWidget().setLayout(self.main_layout) # Delete old layout
            
        self.labels.clear()
        
        if self.layout_type == "horizontal":
            self.main_layout = QHBoxLayout(self.central_widget)
        else:
            self.main_layout = QVBoxLayout(self.central_widget)
            
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        
        for idx in self.selected_indices:
            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("background-color: black;")
            label.setMinimumSize(1, 1)
            self.labels.append((idx, label))
            self.main_layout.addWidget(label)
            
        self.update_aspect_ratio()
        
        # Set initial size if it's the first time
        if not hasattr(self, '_initial_size_set'):
            initial_width = 800
            self.resize(initial_width, int(initial_width / self.aspect_ratio) if self.aspect_ratio else 600)
            self._initial_size_set = True
        else:
            self.apply_aspect_ratio()
            
    def update_aspect_ratio(self):
        if not self.selected_indices:
            self.aspect_ratio = 1
            return
            
        if self.layout_type == "horizontal":
            total_width = sum(self.monitors[idx]['width'] for idx in self.selected_indices)
            max_height = max(self.monitors[idx]['height'] for idx in self.selected_indices)
            self.aspect_ratio = total_width / max_height if max_height else 1
        else:
            max_width = max(self.monitors[idx]['width'] for idx in self.selected_indices)
            total_height = sum(self.monitors[idx]['height'] for idx in self.selected_indices)
            self.aspect_ratio = max_width / total_height if total_height else 1
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # Monitors Submenu
        monitors_menu = menu.addMenu("Monitors")
        monitors_menu.setIcon(create_color_icon("#3498db")) # Blue
        for i, m in enumerate(self.monitors[1:], start=1):
            action = QAction(f"Monitor {i} ({m['width']}x{m['height']})", self)
            action.setCheckable(True)
            action.setChecked(i in self.selected_indices)
            action.setData(i)
            action.triggered.connect(self.toggle_monitor)
            monitors_menu.addAction(action)
            
        # Layout Submenu
        layout_menu = menu.addMenu("Layout")
        layout_menu.setIcon(create_color_icon("#2ecc71")) # Green
        layout_group = QActionGroup(self)
        
        h_action = QAction("Horizontal", self)
        h_action.setCheckable(True)
        h_action.setChecked(self.layout_type == "horizontal")
        h_action.setData("horizontal")
        h_action.triggered.connect(self.change_layout)
        layout_group.addAction(h_action)
        layout_menu.addAction(h_action)
        
        v_action = QAction("Vertical", self)
        v_action.setCheckable(True)
        v_action.setChecked(self.layout_type == "vertical")
        v_action.setData("vertical")
        v_action.triggered.connect(self.change_layout)
        layout_group.addAction(v_action)
        layout_menu.addAction(v_action)
        
        # Swap Monitors (only if exactly 2 are selected)
        if len(self.selected_indices) == 2:
            layout_menu.addSeparator()
            swap_action = QAction("Swap Monitors Order", self)
            swap_action.setIcon(create_color_icon("#e67e22")) # Orange
            swap_action.triggered.connect(self.swap_monitors)
            layout_menu.addAction(swap_action)
        
        # Snap Submenu
        snap_menu = menu.addMenu("Snap to Edge")
        snap_menu.setIcon(create_color_icon("#9b59b6")) # Purple
        snap_group = QActionGroup(self)
        
        snap_options = ["None", "Top Left", "Top Right", "Bottom Left", "Bottom Right", "Top", "Bottom", "Left", "Right"]
        for edge in snap_options:
            action = QAction(edge, self)
            action.setIcon(create_arrow_icon(edge))
            action.setCheckable(True)
            action.setChecked(self.snap_edge == edge)
            action.setData(edge)
            action.triggered.connect(self.change_snap)
            snap_group.addAction(action)
            snap_menu.addAction(action)
        
        menu.addSeparator()
        
        toggle_border_action = QAction("Toggle Borderless", self)
        toggle_border_action.setIcon(create_color_icon("#f1c40f")) # Yellow
        toggle_border_action.triggered.connect(self.toggle_borderless)
        menu.addAction(toggle_border_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setIcon(create_color_icon("#e74c3c")) # Red
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        menu.exec(self.mapToGlobal(pos))
        
    def toggle_monitor(self):
        action = self.sender()
        idx = action.data()
        if action.isChecked():
            if idx not in self.selected_indices:
                self.selected_indices.append(idx)
                self.selected_indices.sort()
        else:
            if idx in self.selected_indices:
                self.selected_indices.remove(idx)
        self.rebuild_layout()
        
    def change_layout(self):
        action = self.sender()
        self.layout_type = action.data()
        self.rebuild_layout()

    def swap_monitors(self):
        if len(self.selected_indices) == 2:
            self.selected_indices.reverse()
            self.rebuild_layout()

    def change_snap(self):
        action = self.sender()
        self.snap_edge = action.data()
        self.apply_snap()
        # Reset snap to None after applying so it doesn't fight manual dragging
        self.snap_edge = "None"

    def apply_snap(self):
        if self.snap_edge == "None":
            return
            
        # Get current screen geometry
        screen = QApplication.screenAt(self.geometry().center())
        if not screen:
            screen = QApplication.primaryScreen()
            
        available_geom = screen.availableGeometry()
        
        x = self.x()
        y = self.y()
        
        if "Top" in self.snap_edge:
            y = available_geom.top()
        elif "Bottom" in self.snap_edge:
            y = available_geom.bottom() - self.height() + 1
            
        if "Left" in self.snap_edge:
            x = available_geom.left()
        elif "Right" in self.snap_edge:
            x = available_geom.right() - self.width() + 1
            
        self.move(x, y)

    def toggle_borderless(self):
        self.is_borderless = not self.is_borderless
        if self.is_borderless:
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        else:
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        # Force layout recalculation and aspect ratio to fix cropping
        QTimer.singleShot(50, self.apply_aspect_ratio)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_borderless:
            self.drag_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.is_borderless:
            diff = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + diff)
            self.drag_pos = event.globalPosition().toPoint()
            
    def resizeEvent(self, event):
        # Start/restart the timer on every resize event
        # This debounces the resize so we don't fight the OS while dragging
        self.resize_timer.start(150)
        super().resizeEvent(event)
        
    def apply_aspect_ratio(self):
        if not self.selected_indices or not self.aspect_ratio:
            return
            
        current_size = self.size()
        target_height = int(current_size.width() / self.aspect_ratio)
        
        # Only resize if the difference is noticeable
        if abs(current_size.height() - target_height) > 2:
            self.resize(current_size.width(), target_height)
            
    def update_frames(self):
        # Get global mouse position
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        for idx, label in self.labels:
            monitor = self.monitors[idx]
            # Capture screen
            sct_img = self.sct.grab(monitor)
            
            # Convert to QImage using BGRA for better performance
            # mss returns BGRA bytes natively on Windows
            bgra_bytes = sct_img.bgra
            img = QImage(bgra_bytes, sct_img.width, sct_img.height, QImage.Format.Format_RGB32)
            
            # Scale pixmap to fit label while keeping aspect ratio
            pixmap = QPixmap.fromImage(img)
            
            # Draw cursor if it's inside this monitor
            if monitor['left'] <= mx < monitor['left'] + monitor['width'] and \
               monitor['top'] <= my < monitor['top'] + monitor['height']:
                
                rel_x = mx - monitor['left']
                rel_y = my - monitor['top']
                
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                # Draw a simple cursor (arrow)
                painter.setPen(QPen(QColor("white"), 2))
                painter.setBrush(QBrush(QColor("black")))
                
                pts = [
                    QPoint(rel_x, rel_y),
                    QPoint(rel_x, rel_y + 20),
                    QPoint(rel_x + 5, rel_y + 15),
                    QPoint(rel_x + 11, rel_y + 25),
                    QPoint(rel_x + 15, rel_y + 23),
                    QPoint(rel_x + 9, rel_y + 13),
                    QPoint(rel_x + 16, rel_y + 13)
                ]
                painter.drawPolygon(QPolygon(pts))
                painter.end()
                
            scaled_pixmap = pixmap.scaled(
                label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
            
    def closeEvent(self, event):
        self.timer.stop()
        self.sct.close()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(create_app_icon())
    
    with mss.mss() as sct:
        monitors = sct.monitors
        
    if len(monitors) <= 1:
        print("No monitors found!")
        return
        
    # Select all monitors except the primary one (index 1)
    selected = list(range(2, len(monitors)))
    if not selected:
        # Fallback if there's only 1 monitor (which shouldn't happen due to the check above, 
        # but just in case mss behaves differently)
        selected = [1]
        
    viewer = ViewerWindow(monitors, selected, "horizontal")
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
