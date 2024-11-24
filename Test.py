import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen
from PyQt6.QtCore import Qt, QTimer, QRect
import random


class DrawingWindow(QMainWindow):
    def __init__(self, coordinates):
        super().__init__()
        self.setWindowTitle("Transparent Drawing Window")

        # Получаем размер экрана через QScreen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

        # Устанавливаем прозрачный фон и безрамочный режим
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.painter = QPainter()
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.pen_color = QColor(255, 0, 0)  # Устанавливаем начальный цвет ручки (красный)
        self.pen_width = 4  # Устанавливаем начальную ширину ручки

        self.coordinates = coordinates  # Сохраняем координаты для рисования прямоугольников

        self.draw_timer = QTimer(self)
        #self.draw_timer.timeout.connect(self.update)  # Подключаем обновление окна к таймеру
        self.draw_timer.start(10)  # Обновляем окно каждые 10 миллисекунд

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setPen(Qt.PenStyle.NoPen)
        self.painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        self.painter.drawRect(QRect(0, 0, self.width(), self.height()))  # Рисуем прозрачный фон

        self.painter.setPen(QPen(QColor(self.pen_color), self.pen_width))
        self.painter.setBrush(QBrush(Qt.GlobalColor.transparent))

        # Рисуем прямоугольники по предоставленным координатам
        for coord in self.coordinates:
            x, y, width, height = coord
            self.painter.drawRect(x, y, width, height)

        self.painter.end()

        self.update_coord()  # Обновляем координаты
        QTimer.singleShot(1000, self.update)  # Планируем перерисовку через 1 секунду

    def update_coord(self, coords=0):
        if coords != 0:
            pass
        else:
            # Генерация случайных координат
            self.coordinates = [
                (random.randrange(0, 500), random.randrange(0, 500),
                 random.randrange(0, 500), random.randrange(0, 500))
            ]


if __name__ == "__main__":
    coordinates = [(524, 474, 818 - 524, 689 - 474), (524, 367, 818 - 524, 473 - 367)]

    app = QApplication(sys.argv)

    # Создаем экземпляр класса DrawingWindow с указанными координатами
    window = DrawingWindow(coordinates)
    window.show()  # Отображаем окно

    sys.exit(app.exec())  # Запускаем цикл событий приложения
