import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QPushButton, QLabel, QInputDialog, QFileDialog, QWidget, QHBoxLayout, QVBoxLayout, QDialog, QGridLayout
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt, QPoint

class PyxelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyxel")
        self.setGeometry(100, 100, 600, 700)
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
        color_button.move(10, 620)

        grid_button = QPushButton("Toggle Grid", self)
        grid_button.clicked.connect(self.toggle_grid)
        grid_button.move(100, 620)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_canvas)
        save_button.move(200, 620)

        self.color_palette = QWidget(self)
        self.color_palette.setGeometry(10, 650, 580, 40)
        self.palette_layout = QHBoxLayout()
        self.color_palette.setLayout(self.palette_layout)
        self.palette_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#FF00FF", "#00FFFF", "#808080", "#FFA500"
        ]
        self.init_color_palette()

        edit_palette_button = QPushButton("Edit Palette", self)
        edit_palette_button.clicked.connect(self.edit_palette)
        edit_palette_button.move(300, 620)

    def init_color_palette(self):
        for color_hex in self.palette_colors:
            color_swatch = QPushButton()
            color_swatch.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #333;")
            color_swatch.setFixedSize(30, 30)
            color_swatch.clicked.connect(lambda _, color=color_hex: self.set_pen_color(color))
            self.palette_layout.addWidget(color_swatch)

    def update_color_palette(self):
        while self.palette_layout.count():
            swatch = self.palette_layout.takeAt(0).widget()
            swatch.deleteLater()
        self.init_color_palette()

    def set_pen_color(self, color_hex):
        self.pen_color = QColor(color_hex)

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

    def edit_palette(self):
        self.temp_palette_colors = self.palette_colors[:]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Color Palette")
        dialog_layout = QGridLayout()
        dialog.setLayout(dialog_layout)

        color_buttons = []
        for index, color_hex in enumerate(self.temp_palette_colors):
            button = QPushButton()
            button.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #333;")
            button.setFixedSize(30, 30)
            button.clicked.connect(lambda _, idx=index, btn=button: self.change_temp_color(idx, btn))
            dialog_layout.addWidget(button, index // 5, index % 5)
            color_buttons.append(button)

        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(lambda: [self.apply_temp_palette(), dialog.accept()])
        dialog_layout.addWidget(confirm_button, len(self.temp_palette_colors) // 5 + 1, 0, 1, 5)
        
        dialog.exec_()

    def change_temp_color(self, index, button):
        color = QColorDialog.getColor()
        if color.isValid():
            self.temp_palette_colors[index] = color.name()
            button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #333;")

    def apply_temp_palette(self):
        self.palette_colors = self.temp_palette_colors
        self.update_color_palette()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyxelApp()
    window.draw_grid()
    window.show()
    sys.exit(app.exec_())
