import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QEventLoop, pyqtSignal, QObject
from FUNCTIONS import *
from SETTINGS import *
import pyautogui
import pygetwindow as gw
import numpy as np
import time
from ui import *

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
connections = [[1, 5], [0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8], [9, 10], [10, 11], [11, 12],
               [13, 14], [14, 15], [15, 16], [13, 17], [17, 18], [18, 19], [19, 20], [0, 17], [5, 9], [9, 13]]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.menu_stat = [self.ui.Status_1, self.ui.Status_2, self.ui.Status_3, self.ui.Status_4]
        self.menu_stat[0].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")

        self.available_cameras = get_available_cameras()
        self.camera_index = min(self.available_cameras)
        self.ui.camera_box.addItems(map(str, self.available_cameras))
        self.ui.camera_box.setCurrentIndex(0)

        self.ui.Menu_button1.clicked.connect(self.select_menu)
        self.ui.Menu_button2.clicked.connect(self.select_menu)
        self.ui.Menu_button3.clicked.connect(self.select_menu)
        self.ui.Menu_button4.clicked.connect(self.select_menu)
        self.ui.pushButton_3.clicked.connect(self.close_window)
        self.ui.pushButton_4.clicked.connect(self.minimize_window)
        self.ui.pushButton.clicked.connect(self.update_tracking)
        self.ui.camera_box.currentIndexChanged.connect(self.update_camera_index)

        self.ui.select_quality.addItems(['high', 'amazing'])
        self.ui.select_quality.setCurrentIndex(0)
        self.ui.select_quality.currentIndexChanged.connect(self.change_model)

        self.ui.show_frame.addItems(['True', 'False'])
        self.ui.show_frame.setCurrentIndex(0)
        self.ui.show_frame.currentIndexChanged.connect(self.change_frame_showing)

        self.ui.bbox_show.addItems(['True', 'False'])
        self.ui.bbox_show.setCurrentIndex(0)
        self.ui.bbox_show.currentIndexChanged.connect(self.change_bbox_show)

        self.is_active = 0

        # Создаем объект Frame
        self.frame_app = Frame()
        self.frame_app.hide()  # Скрываем приложение на старте

    def change_bbox_show(self, index):
        if index == 0:
            self.frame_app.show_bbox = True
        elif index == 1:
            self.frame_app.show_bbox = False

    def change_frame_showing(self, index):
        if index == 0:
            self.frame_app.frame_show = True
        elif index == 1:
            self.frame_app.frame_show = False

    def change_model(self, index):
        self.frame_app.gesture_thread1.set_model(index)


    def update_camera_index(self, index):
        self.camera_index = index
        self.frame_app.gesture_thread1.set_camera_index(self.camera_index)

    def update_tracking(self):
        if self.is_active == 0:
            self.is_active = 1
            self.frame_app.is_active = 1
            self.frame_app.show()  # Показываем Frame
        else:
            self.is_active = 0
            self.frame_app.is_active = 0
            self.frame_app.hide()  # Скрываем Frame

        # self.activation_signal.emit(self.is_active)

    def minimize_window(self):
        self.showMinimized()

    def close_window(self):
        self.close()
        sys.exit()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_position = event.globalPosition().toPoint()  # Запоминаем начальную позицию

    def mouseMoveEvent(self, event):
        if self.old_position:
            delta = event.globalPosition().toPoint() - self.old_position  # Рассчитываем изменение положения
            self.move(self.pos() + delta)  # Перемещаем окно на новое место
            self.old_position = event.globalPosition().toPoint()  # Обновляем начальную позицию

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_position = None  # Очищаем старую позицию

    def select_menu(self):
        clicked_button = self.sender()

        [stat.setStyleSheet("QFrame{background-color: rgb(43, 45, 48);border-radius :12px;}") for stat in
         self.menu_stat]

        if clicked_button is self.ui.Menu_button1:
            self.menu_stat[0].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(0)
        elif clicked_button is self.ui.Menu_button2:
            self.menu_stat[1].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(1)
        elif clicked_button is self.ui.Menu_button3:
            self.menu_stat[2].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(2)
        elif clicked_button is self.ui.Menu_button4:
            self.menu_stat[3].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(3)


class CursorController(QtCore.QThread):
    def __init__(self):
        super().__init__()
        self.target_position = None
        self.running = True
        self.current_gesture = None
        self.prev_position = None
        self.left_button_pressed = False

    def run(self):
        while self.running:
            if self.current_gesture == 4:
                self.handle_selection()

            else:
                if self.left_button_pressed:
                    pyautogui.mouseUp()
                    self.left_button_pressed = False
                # Сброс prev_position при завершении выделения
                self.prev_position = None
                self.target_position = None

            time.sleep(0.01)

    def handle_selection(self):
        """Обрабатывает выделение с помощью текущего жеста."""
        if self.target_position is not None:
            pyautogui.moveTo(self.target_position[8][0], self.target_position[8][1])
            if not self.left_button_pressed:
                pyautogui.mouseDown()
                self.left_button_pressed = True
        else:
            self.prev_position = None

    def update_position(self, position):
        self.prev_position = self.target_position
        self.target_position = position

    def update_gesture(self, gesture):
        self.current_gesture = gesture

    def perform_scroll(self, angle):
        pyautogui.scroll(angle)

    def move_window(self, window, dif):
        window.moveRel(dif[0], dif[1])


class GestureRecognizer(QtCore.QThread):
    gesture_signal = QtCore.pyqtSignal(tuple)

    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.is_runnig = True
        self.width, self.height = screen_width, screen_height
        self.camera_id = 1
        self.capture = cv.VideoCapture(self.camera_id, cv.CAP_DSHOW)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, self.width)  # Ширина кадров в видеопотоке.
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)  # Высота кадров в видеопотоке
        self.classificator = models.load_model('tiny_model.h5')

    def set_model(self, ind):
        print(ind)
        if ind == 0:
            self.classificator = models.load_model('tiny_model.h5')
        elif ind == 1:
            self.classificator = models.load_model('amazing_model.h5')

    def set_camera_index(self, ind):
        self.camera_id = ind
        self.capture = cv.VideoCapture(self.camera_id, cv.CAP_DSHOW)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, self.width)  # Ширина кадров в видеопотоке.
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)  # Высота кадров в видеопотоке
        print(ind)

    def recogniseGesture(self, points):
        result = classification(points, self.classificator)
        cur_gesture, confidence = np.argmax(result), round(np.max(result), 4)  # Результат классификации
        if confidence <= 0.6:
            cur_gesture = 15  # Неопределенный жест, если уверенность низкая
        return cur_gesture

    def run(self):
        while self.is_runnig:
            ret, image = self.capture.read()
            if ret:
                image = cv.flip(image, 1)
                result = hands.process(image)
                if result.multi_hand_landmarks:
                    for hand in result.multi_hand_landmarks:
                        points = np.array(np.array(
                            [(int(hand.landmark[i].x * self.width), int(hand.landmark[i].y * self.height)) for i in
                             range(21)]))

                        gesture = self.recogniseGesture(points)

                        points = fingers_bias(points)

                        self.gesture_signal.emit((gesture, points))
                else:
                    self.gesture_signal.emit((15, None))


class MouseController(QtCore.QThread):
    gesture_signal = QtCore.pyqtSignal(int)
    control_window_signal = QtCore.pyqtSignal(int)  # 0 - скрыть, 1 - заркыть
    scrolling_signal = QtCore.pyqtSignal(int)  # Передает угол наклона
    window_moving_signal = QtCore.pyqtSignal(tuple)  # Переносим окно в передаваемую точку

    def __init__(self, cursor_controller):
        super().__init__()
        self.current_gesture = None
        self.current_points = None
        self.points_normalized = None
        self.is_pressed = False
        self.cursor_controller = cursor_controller

        self.is_scrolling_active = False
        self.angle_to_emit = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.emit_scroll_signal)

    def handle_gesture(self, gesture_info):
        gesture, points = gesture_info
        if points is not None:
            self.points_normalized = return_normalized_points(points)

        if self.current_gesture == 1 and gesture == 0:
            self.click(points[8][0], points[8][1])

        elif self.current_gesture == 3 and gesture == 2:
            self.double_click(points[8][0], points[8][1])

        elif self.current_gesture == 1 and gesture == 7:
            self.right_click(points[8][0], points[8][1])

        elif self.current_gesture == 5 and gesture == 6:
            self.control_window_signal.emit(0)

        elif self.current_gesture == 6 and gesture == 5:
            self.control_window_signal.emit(3)

        elif gesture == 4 and points is not None and self.current_points is not None:
            if dist(self.points_normalized[8][0], self.points_normalized[8][1], self.points_normalized[4][0],
                    self.points_normalized[4][1]) <= 0.45:
                if abs(points[8][0] - self.current_points[8][0]) > 5 or abs(
                        points[8][1] - self.current_points[8][1]) > 5:
                    self.cursor_controller.update_position(points)

        elif gesture == 5 and self.current_gesture == 5 and points is not None and self.current_points is not None:
            if abs(points[8][0] - self.current_points[8][0]) > 5 or abs(
                    points[8][1] - self.current_points[8][1]) > 5:
                self.window_moving_signal.emit(
                    (int(points[8][0] - self.current_points[8][0]), int(points[8][1] - self.current_points[8][1])))

        elif gesture == 13:
            if dist(self.points_normalized[8][0], self.points_normalized[8][1], self.points_normalized[4][0],
                    self.points_normalized[4][1]) <= 0.45:
                angle = int(conversion_to_degrees(calculate_absangle(points)))

                self.angle_to_emit = angle

                if not self.is_scrolling_active:
                    self.timer.start(200)  # Запускаем таймер с интервалом 100 мс
                    self.is_scrolling_active = True  # Устанавливаем флаг, что скроллинг активен

        elif self.is_scrolling_active and gesture != 13:
            self.timer.stop()  # Останавливаем таймер
            self.is_scrolling_active = False  # Сбрасываем флаг активности скроллинга

        if gesture != 15:
            self.current_gesture = gesture

        self.gesture_signal.emit(gesture)
        self.current_points = points

    @staticmethod
    def move_gesture(points):
        pyautogui.moveTo(points[8][0], points[8][1])

    @staticmethod
    def click(point_x, point_y):
        pyautogui.moveTo(point_x, point_y)
        pyautogui.click(button='left')

    @staticmethod
    def right_click(point_x, point_y):
        pyautogui.moveTo(point_x, point_y)
        pyautogui.click(button='right')

    @staticmethod
    def double_click(point_x, point_y):
        pyautogui.moveTo(point_x, point_y)
        pyautogui.doubleClick()

    def emit_scroll_signal(self):
        if self.angle_to_emit is not None:
            self.scrolling_signal.emit(self.angle_to_emit)


class Frame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.finger_points = None
        self.cur_gesture = None
        self.setWindowTitle("Project AltControl")

        self.is_active = 0

        # Получаем размер экрана через QScreen
        screen = QApplication.primaryScreen().geometry()
        self.WIDTH, self.HEIGHT = screen.width(), screen.height()
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        # Устанавливаем прозрачный фон и безрамочный режим
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.selected_window = None

        self.Frame_color = 50

        self.camera_id = 0

        self.frame_show = True

        self.show_bbox = True

        # Создаем потоки
        self.gesture_thread1 = GestureRecognizer(screen.width(), screen.height())
        self.gesture_thread1.gesture_signal.connect(self.on_gesture_detected)
        self.gesture_thread1.start()

        self.cursor_controller = CursorController()
        self.cursor_controller.start()

        self.mouse_thread = MouseController(self.cursor_controller)
        self.mouse_thread.gesture_signal.connect(self.cursor_controller.update_gesture)
        self.mouse_thread.control_window_signal.connect(self.control_window)
        self.mouse_thread.scrolling_signal.connect(self.cursor_controller.perform_scroll)
        self.mouse_thread.window_moving_signal.connect(self.move_window)
        self.gesture_thread1.gesture_signal.connect(self.mouse_thread.handle_gesture)
        self.mouse_thread.start()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_tracking)  # Перерисовываем каждые 20 мс
        self.update_timer.start(20)

    def update_active_flag(self, flag):
        self.is_active = flag

    def update_tracking(self):
        if self.is_active == 1:
            self.update()

    def hide_window(self):
        if self.selected_window is not None:
            self.selected_window.minimize()

    def close_window(self):
        if self.selected_window is not None:
            self.selected_window.minimize()

    def restore_window(self):
        if self.selected_window is not None:
            self.selected_window.minimize()

    def move_window(self, point):
        if self.selected_window is not None:
            self.cursor_controller.move_window(self.selected_window, point)

    def control_window(self, action):
        if action == 0:
            self.hide_window()
        elif action == 1:
            self.close_window()
        elif action == 2:
            self.restore_window()

    def on_gesture_detected(self, result):
        self.finger_points = result[1]
        self.cur_gesture = result[0]
        if self.finger_points is not None:
            try:
                self.selected_window = gw.getWindowsAt(self.finger_points[8][0], self.finger_points[8][1])[1]
            except:
                self.selected_window = None
        else:
            self.selected_window = None

    def paintEvent(self, event):

        painter = QPainter(self)

        # Настраиваем перо и кисть для эллипсов
        pen_ellipses = QPen(QColor(0, 200, 0))  # Цвет с прозрачностью (альфа = 200)
        pen_ellipses.setWidth(3)  # Толщина линий для эллипсов
        painter.setPen(pen_ellipses)

        # Кисть для заливки эллипсов (прозрачная заливка)
        brush_ellipses = QColor(0, 200, 0)  # Полупрозрачный синий
        painter.setBrush(brush_ellipses)
        if self.finger_points is not None:
            # Рисуем эллипсы для всех точек
            for point in self.finger_points:
                painter.drawEllipse(QPoint(point[0], point[1]), 7, 7)  # Радиус эллипсов = 5

            # Настраиваем перо для линий (соединений)
            pen_lines = QPen(QColor(0, 200, 0))  # Зеленый с прозрачностью (альфа = 150)
            pen_lines.setWidth(4)  # Толщина линий для соединений
            painter.setPen(pen_lines)

            # Рисуем соединения
            for connection in connections:
                painter.drawLine(QPoint(self.finger_points[connection[0]][0], self.finger_points[connection[0]][1]),
                                 QPoint(self.finger_points[connection[1]][0], self.finger_points[connection[1]][1]))

            if self.show_bbox == True:
                painter.setPen(QColor(0, 170, 0))
                painter.setBrush(Qt.GlobalColor.transparent)

                bbox = bbox_cords(self.finger_points)
                painter.drawRect(QRect(bbox[0], bbox[1], bbox[2], bbox[3]))
                text = gestures[self.cur_gesture]  # Текст, который нужно отобразить
                font = painter.font()  # Получаем текущий шрифт
                font.setPointSize(20)  # Устанавливаем размер шрифта
                painter.setFont(font)  # Применяем шрифт к painter
                painter.drawText(QPoint(bbox[0], bbox[1] - 10), text)

            if self.Frame_color <= 200:
                self.Frame_color += 1

        else:
            if self.Frame_color >= 10:
                self.Frame_color -= 1
        pen = QPen(QColor(0, self.Frame_color, 0, 200))  # Создаем QPen с цветом
        pen.setWidth(int(np.log(self.Frame_color) * np.sin(
            self.Frame_color / 15) ** 2 + self.Frame_color / 50))  # Устанавливаем ширину пера
        painter.setPen(pen)  # Устанавливаем pen для painter
        painter.setBrush(Qt.GlobalColor.transparent)  # Устанавливаем прозрачную заливку

        # Рисуем прямоугольник с помощью painter
        if self.frame_show:
            painter.drawRect(QRect(3, 3, WIDTH - 5, HEIGHT - 50))

        if self.selected_window is not None:
            if self.selected_window.isMinimized is not False:
                painter.drawRect(QRect(
                    self.selected_window.left,
                    self.selected_window.top,
                    self.selected_window.width,
                    self.selected_window.height
                ))

        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Создаем экземпляр главного окна
    main_window = MainWindow()

    # Показываем главное окно
    main_window.show()
    sys.exit(app.exec())
