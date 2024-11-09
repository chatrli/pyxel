import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QPushButton, QLabel, QInputDialog, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt, QPoint

class PyxelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyxel")
        self.setGeometry(100, 100, 600, 650)
        self.pixel_size = 10
        self.canvas_width = 580 // self.pixel_size * self.pixel_size
        self.canvas_height = 580 // self.pixel_size * self.pixel_size

        self.canvas = QLabel(self)
        self.canvas.setGeometry(10, 10, self.canvas_width, self.canvas_height)
        self.main_pixmap = QPixmap(self.canvas.size())
        self.main_pixmap.fill(Qt.white)
        self.grid_overlay = QPixmap(self.canvas.size())
        self.grid_overlay.fill(Qt.transparent)

        self.canvas.setPixmap(self.main_pixmap)

        self.pen_color = QColor(Qt.black)
        self.drawing = False
        self.show_grid = False

        color_button = QPushButton("Select Color", self)
        color_button.clicked.connect(self.select_color)
        color_button.move(10, 600)

        grid_button = QPushButton("Toggle Grid", self)
        grid_button.clicked.connect(self.toggle_grid)
        grid_button.move(100, 600)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_canvas)
        save_button.move(200, 600)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.update_canvas()

    def update_canvas(self):
        combined_pixmap = QPixmap(self.main_pixmap)

        if self.show_grid:
            combined_painter = QPainter(combined_pixmap)
            combined_painter.drawPixmap(0, 0, self.grid_overlay)
            combined_painter.end()

        self.canvas.setPixmap(combined_pixmap)

    def draw_grid(self):
        self.grid_overlay.fill(Qt.transparent)
        painter = QPainter(self.grid_overlay)
        pen = QPen(Qt.lightGray)
        pen.setWidth(1)
        painter.setPen(pen)

        for x in range(0, self.canvas_width, self.pixel_size):
            painter.drawLine(x, 0, x, self.canvas_height)

        for y in range(0, self.canvas_height, self.pixel_size):
            painter.drawLine(0, y, self.canvas_width, y)

        painter.end()

    def get_pixel_position(self, pos):
        x = (pos.x() // self.pixel_size) * self.pixel_size
        y = (pos.y() // self.pixel_size) * self.pixel_size
        return QPoint(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.draw_pixel(event.pos())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            self.draw_pixel(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def draw_pixel(self, pos):
        pixel_pos = self.get_pixel_position(pos - self.canvas.pos())
        
        painter = QPainter(self.main_pixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.pen_color)
        painter.drawRect(pixel_pos.x(), pixel_pos.y(), self.pixel_size, self.pixel_size)
        
        painter.end()
        self.update_canvas()

    def save_canvas(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", options=options)
        
        if file_path:
            self.main_pixmap.save(file_path)
            print(f"Image saved to {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyxelApp()
    window.draw_grid()
    window.show()
    sys.exit(app.exec_())
