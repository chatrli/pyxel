import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QPushButton, QLabel, QInputDialog, QFileDialog, QWidget, QHBoxLayout, QVBoxLayout, QDialog, QGridLayout, QListWidget, QListWidgetItem, QSlider
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QPoint

class PyxelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyxel")
        self.setGeometry(100, 100, 600, 750)
        self.pixel_size = 10
        self.canvas_width = 580 // self.pixel_size * self.pixel_size
        self.canvas_height = 580 // self.pixel_size * self.pixel_size

        # setup canvas
        self.canvas = QLabel(self)
        self.canvas.setGeometry(10, 10, self.canvas_width, self.canvas_height)
        self.grid_overlay = QPixmap(self.canvas.size())
        self.grid_overlay.fill(Qt.transparent)

        # setup layer
        self.layers = [QPixmap(self.canvas.size())]
        self.layers[0].fill(Qt.white)
        self.current_layer_index = 0
        self.canvas.setPixmap(self.layers[0])

        # drawing default settings
        self.pen_color = QColor(Qt.black)
        self.drawing = False
        self.show_grid = False
        self.draw_size = 10

        # buttons
        self.buttons()

        # setup default color palette
        self.color_palette = QWidget(self)
        self.color_palette.setGeometry(10, 650, 580, 40)
        self.palette_layout = QHBoxLayout()
        self.color_palette.setLayout(self.palette_layout)
        self.palette_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#FF00FF", "#00FFFF", "#808080", "#FFA500"
        ]
        self.init_color_palette()


    def buttons(self):
        # select a color
        color_button = QPushButton("Color", self)
        color_button.clicked.connect(self.select_color)
        color_button.move(0, 620)
        color_button.setShortcut(QKeySequence('shift+c'))

        # toggle grid on canvas (on/off)
        grid_button = QPushButton("Grid", self)
        grid_button.clicked.connect(self.toggle_grid)
        grid_button.move(100, 620)
        grid_button.setShortcut(QKeySequence('shift+g'))

        # save the file with all layers (save locally)
        save_button = QPushButton("Save As File", self)
        save_button.clicked.connect(self.save_canvas)
        save_button.move(200, 620)
        save_button.setShortcut(QKeySequence('ctrl+shift+s'))

        # edit the color palette
        edit_palette_button = QPushButton("Edit Palette", self)
        edit_palette_button.clicked.connect(self.edit_palette)
        edit_palette_button.move(300, 620)
        edit_palette_button.setShortcut(QKeySequence('ctrl+shift+c'))

        # add a layer
        add_layer_button = QPushButton("+ Layer", self)
        add_layer_button.clicked.connect(self.add_layer)
        add_layer_button.move(400, 620)

        # remove a layer
        remove_layer_button = QPushButton("- Layer", self)
        remove_layer_button.clicked.connect(self.remove_layer)
        remove_layer_button.move(500, 620)

        # show all layers (layer is clickable)
        self.layer_list = QListWidget(self)
        self.layer_list.setGeometry(500, 10, 80, 580)
        self.layer_list.itemClicked.connect(self.select_layer)
        self.update_layer_list()

        # draw size (10 = 1px)
        draw_size_slider = QSlider(Qt.Horizontal, self)
        draw_size_slider.setGeometry(0, 590, 100, 30)
        draw_size_slider.setMinimum(0)
        draw_size_slider.setMaximum(100)
        draw_size_slider.setValue(10)
        draw_size_slider.setTickInterval(10)
        draw_size_slider.valueChanged.connect(self.update_draw_size)

    def init_color_palette(self):
        for color_hex in self.palette_colors:
            color_swatch = QPushButton()
            color_swatch.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #333;")
            color_swatch.setFixedSize(100, 100)
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
        combined_pixmap = QPixmap(self.canvas.size())
        combined_pixmap.fill(Qt.white)
        combined_painter = QPainter(combined_pixmap)

        for layer in self.layers:
            combined_painter.drawPixmap(0, 0, layer)

        if self.show_grid:
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
        painter = QPainter(self.layers[self.current_layer_index])
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.pen_color)
        painter.drawRect(pixel_pos.x(), pixel_pos.y(), self.draw_size, self.draw_size)
        painter.end()
        self.update_canvas()

    def save_canvas(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As File", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", options=options)
        
        if file_path:
            combined_pixmap = QPixmap(self.canvas.size())
            combined_pixmap.fill(Qt.white)
            painter = QPainter(combined_pixmap)
            for layer in self.layers:
                painter.drawPixmap(0, 0, layer)
            painter.end()
            combined_pixmap.save(file_path)
            print(f"File saved to {file_path}")

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

    def add_layer(self):
        new_layer = QPixmap(self.canvas.size())
        new_layer.fill(Qt.transparent)
        self.layers.append(new_layer)
        self.current_layer_index = len(self.layers) - 1
        self.update_layer_list()
        self.update_canvas()

    def remove_layer(self):
        if len(self.layers) > 1:
            del self.layers[self.current_layer_index]
            self.current_layer_index = max(0, self.current_layer_index - 1)
            self.update_layer_list()
            self.update_canvas()

    def select_layer(self, item):
        self.current_layer_index = self.layer_list.row(item)
        self.update_canvas()

    def update_layer_list(self):
        self.layer_list.clear()
        for i, layer in enumerate(self.layers):
            item = QListWidgetItem(f"Layer {i + 1}")
            self.layer_list.addItem(item)
        self.layer_list.setCurrentRow(self.current_layer_index)

    def update_draw_size(self, value):
        self.draw_size = value


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyxelApp()
    window.draw_grid()
    window.show()
    sys.exit(app.exec_())
