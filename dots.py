#!/usr/bin/env python3
from math import sin, cos, radians, degrees
from PyQt5.QtGui import QPainter, QPalette, QPen, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QApplication
from PyQt5.QtCore import QSize, QRectF, QTimer, QPointF

class CircleWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setBackgroundRole(QPalette.Base)
        # self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame_no: int = 0

    def minimumSizeHint(self):
        return QSize(50,50)

    def sizeHint(self):
        return QSize(180,180)

    def next_animation_frame(self):
        self.frame_no += 1
        self.update()

    def paintEvent(self, QPaintEvent):
        pain = QPainter(self)
        pain.setRenderHint(QPainter.Antialiasing, True)

        pain.translate(self.width()/2, self.height() /2)

        for diameter in range(0, 256, 9):
            delta = abs((self.frame_no % 128) - diameter / 2)
            alpha = 255 - (delta**2) / 4 - diameter
            if alpha > 0:
                pain.setPen(QPen(QColor(0, diameter / 2, 127, alpha), 3))
                pain.drawEllipse(QRectF(-diameter / 2, -diameter / 2, diameter, diameter))


class DotsWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setBackgroundRole(QPalette.Base)
        # self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame_no: int = 90

    def minimumSizeHint(self):
        return QSize(50,50)

    def sizeHint(self):
        return QSize(180,180)

    def next_animation_frame(self):
        self.frame_no += 1
        self.update()

    def paintEvent(self, QPaintEvent):
        pain = QPainter(self)
        pain.setRenderHint(QPainter.Antialiasing, True)
        pain.translate(self.width()/2, self.height() /2)
        pain.setPen(QPen(QColor(10,10,10), 3))

        halfmax = 180
        max_dot_num = 8
        for dot_num in range(max_dot_num):
            angle_off = radians(360/max_dot_num) * dot_num
            green = ((255/max_dot_num)-1) * (max_dot_num - dot_num)
            blue = ((255/max_dot_num)-1) * dot_num
            pain.setPen(QPen(QColor(0, green, blue), 3))
            progress = (cos(radians(3 * self.frame_no)) + 1)/2 * 180
            # Progress dictates the range of values of x later fed into cos(x)
            # frame_no multiplier dictates frequency of oscillations
            # Progress left side goes between 0 and 1, so overall goes between
            # 0 and 180 which later gives us a cos(progress) ranging between
            # 1 and -1, which combines with sometimes-neg wid * hei to give a full range
            # print(self.frame_no,progress)
            height = sin(angle_off) * self.height()
            width = cos(angle_off) * self.width()
            # (0,0) is the centre
            x = cos(radians(progress)) * width / 2
            y = cos(radians(progress)) * height / 2

            pain.drawEllipse(QPointF(x, y), 2, 2)


class Window(QWidget):
    def __init__(self):
        super().__init__(None)
        layout = QVBoxLayout(self)
        # circlewid = CircleWidget()
        timer = QTimer(self)
        # timer.timeout.connect(circlewid.next_animation_frame)
        # layout.addWidget(circlewid)
        dotwid = DotsWidget()
        timer.timeout.connect(dotwid.next_animation_frame)
        layout.addWidget(dotwid)
        timer.start(20)
        # self.setLayout(layout)

def main():
    app = QApplication([])
    win = Window()
    win.show()
    return app.exec()

if __name__ == '__main__':
    main()
