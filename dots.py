#!/usr/bin/env python3
from math import sin, cos, radians
from PyQt5.QtGui import QPainter, QPalette, QPen, QColor, QBrush
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QSizePolicy,
                             QApplication, QSlider, QLabel, QPushButton)
from PyQt5.QtCore import QSize, QTimer, QPointF, Qt

SAVING = False
# SAVING = True
SPEED_MULT = 4


class DotsWidget(QWidget):

    def __init__(self):
        super().__init__()
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor("#fff"))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.frame_no: int = 1
        self.angle_factor = 360 # related to degrees offset of each dot
        self.num_dots = 40
        self.dot_size = 6
        self.x_multiplier = 1
        self.y_multiplier = 1

    def minimumSizeHint(self):
        return QSize(50,50)

    def sizeHint(self):
        return QSize(400,400)

    def change_angle_factor(self, value):
        self.parent().a_f_slider_val_label.setText(str(value))
        self.angle_factor = value

    def change_num_dots(self, value):
        self.parent().num_dots_slider_val_label.setText(str(value))
        self.num_dots = value

    def change_dot_size(self, value):
        self.parent().dot_size_slider_val_label.setText(str(value))
        self.dot_size = value

    def change_x_multiplier(self, value):
        self.parent().x_multiplier_slider_val_label.setText(str(value))
        self.x_multiplier = value

    def change_y_multiplier(self, value):
        self.parent().y_multiplier_slider_val_label.setText(str(value))
        self.y_multiplier = value

    def next_animation_frame(self):
        if SAVING:
            self.grab().save('gifs/1/img{0:03d}.png'.format(self.frame_no), None, 100)
            # if self.frame_no > 360/SPEED_MULT:
            if self.frame_no >= 360 /SPEED_MULT:
                self.timer.stop()
                self.parent().close()
        else:
            self.update()
        self.frame_no += 1

    def paintEvent(self, QPaintEvent):
        pain = QPainter(self)
        pain.setRenderHint(QPainter.Antialiasing, True)
        pain.translate(self.width()/2, self.height() /2)
        pain.setPen(QPen(QColor(10,10,10), 3))

        for cur_dot_num in range(self.num_dots):
            frame_no = self.frame_no + cur_dot_num*(180/self.num_dots)/SPEED_MULT
            angle_off = radians(self.angle_factor/self.num_dots) * cur_dot_num
            green = ((255/self.num_dots)-1) * (self.num_dots - cur_dot_num)
            blue = ((255/self.num_dots)-1) * cur_dot_num
            colour = QColor(0, green, blue)
            pain.setPen(QPen(colour))
            pain.setBrush(QBrush(colour))
            progress = (cos(radians(SPEED_MULT * frame_no)) + 1)/2 * 180
            # Progress oscillates every 360/speed_mult frames
            # Progress dictates the range of values of x later fed into cos(x)
            # frame_no multiplier dictates frequency of oscillations
            # Progress left side goes between 0 and 1, so overall goes between
            # 0 and 180 which later gives us a cos(progress) ranging between
            # 1 and -1, which combines with sometimes-neg wid * hei to give a full range
            # print(self.frame_no,progress)
            height = sin(angle_off) * (self.height() - 100)
            width = cos(angle_off) * (self.width() - 100)
            # (0,0) is the centre
            x = cos(radians(self.x_multiplier * progress)) * width / 2
            y = cos(radians(self.y_multiplier * progress)) * height / 2

            pain.drawEllipse(QPointF(x, y), self.dot_size, self.dot_size)

class Window(QWidget):
    def __init__(self):
        super().__init__(None)
        layout = QVBoxLayout(self)
        # circlewid = CircleWidget()
        # timer.timeout.connect(circlewid.next_animation_frame)
        # layout.addWidget(circlewid)
        self.dotwid = DotsWidget()
        self.dotwid.timer = QTimer(self)
        self.dotwid.timer.timeout.connect(self.dotwid.next_animation_frame)
        layout.addWidget(self.dotwid)
        controls_box =  QFormLayout()

        angle_factor_box = QHBoxLayout()
        self.angle_factor_slider = QSlider(Qt.Horizontal)
        self.angle_factor_slider.setMaximum(1080)
        self.angle_factor_slider.setValue(360)
        self.a_f_slider_val_label = QLabel(str(self.angle_factor_slider.value()))
        self.angle_factor_slider.valueChanged.connect(self.dotwid.change_angle_factor)
        # num dots, col dots - gradient
        angle_factor_box.addWidget(self.angle_factor_slider)
        angle_factor_box.addWidget(self.a_f_slider_val_label)
        controls_box.addRow("Angle Factor", angle_factor_box)

        num_dots_box = QHBoxLayout()
        self.num_dots_slider = QSlider(Qt.Horizontal)
        self.num_dots_slider.setMaximum(120)
        self.num_dots_slider.setValue(40)
        self.num_dots_slider.valueChanged.connect(self.dotwid.change_num_dots)
        self.num_dots_slider_val_label = QLabel(str(self.num_dots_slider.value()))
        num_dots_box.addWidget(self.num_dots_slider)
        num_dots_box.addWidget(self.num_dots_slider_val_label)
        controls_box.addRow("Dot number", num_dots_box)

        dot_size_box = QHBoxLayout()
        self.dot_size_slider = QSlider(Qt.Horizontal)
        self.dot_size_slider.setMaximum(40)
        self.dot_size_slider.setValue(6)
        self.dot_size_slider.valueChanged.connect(self.dotwid.change_dot_size)
        self.dot_size_slider_val_label = QLabel(str(self.dot_size_slider.value()))
        dot_size_box.addWidget(self.dot_size_slider)
        dot_size_box.addWidget(self.dot_size_slider_val_label)
        controls_box.addRow("Dot size", dot_size_box)

        x_multiplier_box = QHBoxLayout()
        self.x_multiplier_slider = QSlider(Qt.Horizontal)
        self.x_multiplier_slider.setMaximum(10)
        self.x_multiplier_slider.setValue(1)
        self.x_multiplier_slider.valueChanged.connect(self.dotwid.change_x_multiplier)
        self.x_multiplier_slider_val_label = QLabel(str(self.x_multiplier_slider.value()))
        x_multiplier_box.addWidget(self.x_multiplier_slider)
        x_multiplier_box.addWidget(self.x_multiplier_slider_val_label)
        controls_box.addRow("X Multiplier", x_multiplier_box)

        y_multiplier_box = QHBoxLayout()
        self.y_multiplier_slider = QSlider(Qt.Horizontal)
        self.y_multiplier_slider.setMaximum(10)
        self.y_multiplier_slider.setValue(1)
        self.y_multiplier_slider.valueChanged.connect(self.dotwid.change_y_multiplier)
        self.y_multiplier_slider_val_label = QLabel(str(self.y_multiplier_slider.value()))
        y_multiplier_box.addWidget(self.y_multiplier_slider)
        y_multiplier_box.addWidget(self.y_multiplier_slider_val_label)
        controls_box.addRow("Y Multiplier", y_multiplier_box)

        speed_box = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        # self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.speed_slider_val_label = QLabel(str(self.speed_slider.value()))
        speed_box.addWidget(self.speed_slider)
        speed_box.addWidget(self.speed_slider_val_label)
        controls_box.addRow("Speed", speed_box)

        reset_button = QPushButton("Reset values")
        reset_button.pressed.connect(self.reset_controls)

        controls_box.addWidget(reset_button)
        controls_widget = QWidget(self)
        controls_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor("#b5b5b5"))
        controls_widget.setPalette(pal)
        controls_widget.setAutoFillBackground(True)
        controls_widget.setLayout(controls_box)

        layout.addWidget(controls_widget)
        if SAVING:
            self.dotwid.timer.start(1)
        else:
            self.dotwid.timer.start(100/5)
        # self.setLayout(layout)

        # TODO toggle showing settings, axis lines & toggle, jerkiness fix, colours
        # TODO not have to change default values in multiple places (DotWidget, sliders, reset)

    def change_speed(self, value):
        if value == 0:
            self.dotwid.timer.stop()
            return
        self.dotwid.timer.start(100/value)
        self.speed_slider_val_label.setText(str(value))

    def reset_controls(self, *args):
        self.speed_slider.setValue(5)
        self.x_multiplier_slider.setValue(1)
        self.y_multiplier_slider.setValue(1)
        self.dot_size_slider.setValue(6)
        self.num_dots_slider.setValue(40)
        self.angle_factor_slider.setValue(360)

def main():
    app = QApplication([])
    win = Window()
    win.show()
    return app.exec()

if __name__ == '__main__':
    main()
