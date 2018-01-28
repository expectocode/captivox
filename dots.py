#!/usr/bin/env python3
from math import sin, cos, radians
from time import sleep
from PyQt5.QtGui import QPainter, QPalette, QPen, QColor, QBrush
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
                             QSizePolicy, QApplication, QSlider, QLabel,
                             QPushButton, QCheckBox, QSpacerItem, QFileDialog,
                             QMessageBox, QProgressDialog)
from PyQt5.QtCore import QSize, QTimer, QPointF, Qt, \
                         QLineF, QByteArray, QBuffer, QIODevice
EXPORT_AVAILABLE = True
try:
    import imageio
except ImportError:
    print("Animation video export will be unavailable")
    EXPORT_AVAILABLE = False

# Default values of various options
X_MULT_DEF = 1
Y_MULT_DEF = 1
DOT_SIZE_DEF = 6
NUM_DOTS_DEF = 40
ANGLE_FACTOR_DEF = 360
HALFMAX_DEF = 180
SPEED_MULT_DEF = 3
FRAMERATE_DEF = 5
AXES_DEF = False


class DotsWidget(QWidget):
    """A custom widget for animating dots"""

    def __init__(self):
        super().__init__()
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor("#fff"))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.frame_no = 1
        self.angle_factor = ANGLE_FACTOR_DEF  # related to degrees offset of each dot
        self.num_dots = NUM_DOTS_DEF
        self.dot_size = DOT_SIZE_DEF
        self.x_multiplier = X_MULT_DEF
        self.y_multiplier = Y_MULT_DEF
        self.halfmax = HALFMAX_DEF
        self.speedmult = SPEED_MULT_DEF
        self.draw_axes = AXES_DEF

    def minimumSizeHint(self):
        """Must be implemented"""
        return QSize(50, 50)

    def sizeHint(self):
        """Must be implemented"""
        return QSize(400, 400)

    def change_angle_factor(self, value):
        """Take slider input and reflect the new value in the label"""
        self.parent().a_f_slider_val_label.setText(str(value))
        self.angle_factor = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def change_halfmax(self, value):
        """Take slider input and reflect the new value in the label"""
        self.parent().halfmax_slider_val_label.setText(str(value))
        self.halfmax = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def change_speedmult(self, value):
        """Take slider input and reflect the new value in the label"""
        self.parent().speedmult_slider_val_label.setText(str(value))
        self.speedmult = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def change_draw_axes(self, value):
        """Take checkbox input"""
        self.draw_axes = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def change_num_dots(self, value):
        """Take slider input and reflect the new value in the label"""
        self.parent().num_dots_slider_val_label.setText(str(value))
        self.num_dots = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def change_dot_size(self, value):
        """Take slider input and reflect the new value in the label"""
        self.parent().dot_size_slider_val_label.setText(str(value))
        self.dot_size = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def change_x_multiplier(self, value):
        """Take slider input and reflect the new value in the label"""
        self.parent().x_multiplier_slider_val_label.setText(str(value))
        self.x_multiplier = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def change_y_multiplier(self, value):
        """Take slider input and reflect the new value in the label"""
        self.parent().y_multiplier_slider_val_label.setText(str(value))
        self.y_multiplier = value
        if self.parent().framerate_slider.value() == 0:
            self.frame_no -= 1
            self.next_animation_frame()

    def next_animation_frame(self):
        """Connects to the timer to fire the animation"""
        self.update()
        self.frame_no += 1

    def export_video(self):
        """Record and save a mp4 video of the current animation"""
        if not EXPORT_AVAILABLE:
            msgbox = QMessageBox(QMessageBox.Information,
                                 "Export not available",
                                 "You need to install `imageio` to export videos")
            msgbox.exec()
            return

        location = QFileDialog.getSaveFileName(self,
                                               "Choose export location",
                                               filter="Video (*.mp4)")
        location = location[0]
        if location == '':
            # No file selected
            msgbox = QMessageBox(QMessageBox.Information,
                                 "Export cancelled",
                                 "No export file given")
            msgbox.exec()
            return

        if not location.endswith('.mp4'):
            location += '.mp4'
        progress_box = QProgressDialog(
            "Recording export video.\nNote that the larger the Period, "
            "the longer the video.",
            "Cancel",
            1,
            self.halfmax * 2 + 1,
            self)
        progress_box.setWindowModality(Qt.WindowModal)
        sleep(0.2)  # sometimes the progressbox wouldn't show. this seems to fix
        duration = self.timer.interval()
        with imageio.get_writer(location, format='mp4', mode='I', fps=1000/duration) as writer:
            self.frame_no = 1
            for i in range(self.halfmax * 2 + 1):
                progress_box.setValue(i)
                if progress_box.wasCanceled():
                    return
                print(i)
                im_bytes = QByteArray()
                buf = QBuffer(im_bytes)
                buf.open(QIODevice.WriteOnly)
                self.grab().save(buf, 'PNG', 100)
                self.frame_no += 1
                # self.update()
                # frames.append(imageio.imread(im_bytes.data(), 'png'))
                writer.append_data(imageio.imread(im_bytes.data(), 'png'))
        progress_box.setValue(progress_box.maximum())

        msgbox = QMessageBox(QMessageBox.Information,
                             "Information",
                             "Export finished! Saved to {}".format(location))
        msgbox.exec()

    def paintEvent(self, *_):
        """
        This is called on self.update() and on resize - makes resizes a bit ugly.
        This method draws every frame and forms the core of the program.
        """
        pain = QPainter(self)
        pain.setRenderHint(QPainter.Antialiasing, True)
        pain.translate(self.width() / 2, self.height() / 2)  # Make (0,0) centre

        if self.draw_axes:
            pain.setPen(QPen(QColor(0, 0, 0, 64), 1))
            # Line(x1,y2,x2,y2)
            pain.drawLine(QLineF(0, self.height() / 2, 0, -self.height() / 2))
            pain.drawLine(QLineF(self.width() / 2, 0, -self.width() / 2, 0))

        for cur_dot_num in range(self.num_dots):
            frame_no = self.frame_no + cur_dot_num*(180/self.num_dots)/self.speedmult
            angle_off = radians(self.angle_factor/self.num_dots) * cur_dot_num
            green = (240/self.num_dots) * (self.num_dots - cur_dot_num)
            blue = (240/self.num_dots) * cur_dot_num
            colour = QColor(0, green, blue)
            pain.setPen(QPen(colour))
            pain.setBrush(QBrush(colour))
            # progress = (cos(radians(SPEED_MULT * frame_no)) + 1)/2 * 180
            progress = abs((frame_no * self.speedmult) % (2*self.halfmax)-self.halfmax)
            # Progress oscillates every 360/speed_mult frames
            # Progress dictates the range of values of x later fed into cos(x)
            # frame_no multiplier dictates frequency of oscillations
            # Progress ranges between 0 and 180 which later gives us a
            # cos(progress) ranging between # 1 and -1, which combines with
            # sometimes-neg wid * hei to give a full range
            # print(self.frame_no,progress)
            height = sin(angle_off) * (self.height() - 100)
            width = cos(angle_off) * (self.width() - 100)
            # (0,0) is the centre
            x = cos(radians(self.x_multiplier * progress)) * width / 2
            y = cos(radians(self.y_multiplier * progress)) * height / 2

            pain.drawEllipse(QPointF(x, y), self.dot_size, self.dot_size)


class Halcyon(QWidget):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("Halcyon")
        layout = QVBoxLayout(self)
        self.dotwid = DotsWidget()
        self.dotwid.timer = QTimer(self)
        self.dotwid.timer.timeout.connect(self.dotwid.next_animation_frame)
        layout.addWidget(self.dotwid)
        controls_box = QFormLayout()

        angle_factor_box = QHBoxLayout()
        self.angle_factor_slider = QSlider(Qt.Horizontal)
        self.angle_factor_slider.setMaximum(1080)
        self.angle_factor_slider.setValue(ANGLE_FACTOR_DEF)
        self.a_f_slider_val_label = QLabel(str(self.angle_factor_slider.value()))
        self.angle_factor_slider.valueChanged.connect(self.dotwid.change_angle_factor)
        angle_factor_box.addWidget(self.angle_factor_slider)
        angle_factor_box.addWidget(self.a_f_slider_val_label)
        controls_box.addRow("Angle Factor", angle_factor_box)

        num_dots_box = QHBoxLayout()
        self.num_dots_slider = QSlider(Qt.Horizontal)
        self.num_dots_slider.setMaximum(200)
        self.num_dots_slider.setValue(NUM_DOTS_DEF)
        self.num_dots_slider.valueChanged.connect(self.dotwid.change_num_dots)
        self.num_dots_slider_val_label = QLabel(str(self.num_dots_slider.value()))
        num_dots_box.addWidget(self.num_dots_slider)
        num_dots_box.addWidget(self.num_dots_slider_val_label)
        controls_box.addRow("Dot number", num_dots_box)

        dot_size_box = QHBoxLayout()
        self.dot_size_slider = QSlider(Qt.Horizontal)
        self.dot_size_slider.setMaximum(40)
        self.dot_size_slider.setValue(DOT_SIZE_DEF)
        self.dot_size_slider.valueChanged.connect(self.dotwid.change_dot_size)
        self.dot_size_slider_val_label = QLabel(str(self.dot_size_slider.value()))
        dot_size_box.addWidget(self.dot_size_slider)
        dot_size_box.addWidget(self.dot_size_slider_val_label)
        controls_box.addRow("Dot size", dot_size_box)

        x_multiplier_box = QHBoxLayout()
        self.x_multiplier_slider = QSlider(Qt.Horizontal)
        self.x_multiplier_slider.setMaximum(10)
        self.x_multiplier_slider.setValue(X_MULT_DEF)
        self.x_multiplier_slider.valueChanged.connect(self.dotwid.change_x_multiplier)
        self.x_multiplier_slider_val_label = QLabel(str(self.x_multiplier_slider.value()))
        x_multiplier_box.addWidget(self.x_multiplier_slider)
        x_multiplier_box.addWidget(self.x_multiplier_slider_val_label)
        controls_box.addRow("X Multiplier", x_multiplier_box)

        y_multiplier_box = QHBoxLayout()
        self.y_multiplier_slider = QSlider(Qt.Horizontal)
        self.y_multiplier_slider.setMaximum(10)
        self.y_multiplier_slider.setValue(Y_MULT_DEF)
        self.y_multiplier_slider.valueChanged.connect(self.dotwid.change_y_multiplier)
        self.y_multiplier_slider_val_label = QLabel(str(self.y_multiplier_slider.value()))
        y_multiplier_box.addWidget(self.y_multiplier_slider)
        y_multiplier_box.addWidget(self.y_multiplier_slider_val_label)
        controls_box.addRow("Y Multiplier", y_multiplier_box)

        halfmax_box = QHBoxLayout()
        self.halfmax_slider = QSlider(Qt.Horizontal)
        self.halfmax_slider.setMinimum(1)
        self.halfmax_slider.setMaximum(720)
        self.halfmax_slider.setValue(HALFMAX_DEF)
        self.halfmax_slider.valueChanged.connect(self.dotwid.change_halfmax)
        self.halfmax_slider_val_label = QLabel(str(self.halfmax_slider.value()))
        halfmax_box.addWidget(self.halfmax_slider)
        halfmax_box.addWidget(self.halfmax_slider_val_label)
        controls_box.addRow("Period", halfmax_box)

        framerate_box = QHBoxLayout()
        self.framerate_slider = QSlider(Qt.Horizontal)
        self.framerate_slider.setMaximum(10)
        self.framerate_slider.setValue(5)
        self.framerate_slider.valueChanged.connect(self.change_framerate)
        self.framerate_slider_val_label = QLabel(str(self.framerate_slider.value()))
        framerate_box.addWidget(self.framerate_slider)
        framerate_box.addWidget(self.framerate_slider_val_label)
        controls_box.addRow("Framerate", framerate_box)

        speedmult_box = QHBoxLayout()
        self.speedmult_slider = QSlider(Qt.Horizontal)
        self.speedmult_slider.setMinimum(1)
        self.speedmult_slider.setMaximum(12)
        self.speedmult_slider.setValue(SPEED_MULT_DEF)
        self.speedmult_slider.valueChanged.connect(self.dotwid.change_speedmult)
        self.speedmult_slider_val_label = QLabel(str(self.speedmult_slider.value()))
        speedmult_box.addWidget(self.speedmult_slider)
        speedmult_box.addWidget(self.speedmult_slider_val_label)
        controls_box.addRow("Speed", speedmult_box)

        self.draw_axes_checkbox = QCheckBox("Show axes")
        self.draw_axes_checkbox.stateChanged.connect(self.dotwid.change_draw_axes)
        # controls_box.addWidget(self.draw_axes_checkbox)

        reset_button = QPushButton("Reset values")
        reset_button.pressed.connect(self.reset_controls)

        export_button = QPushButton("Export a video")
        export_button.pressed.connect(self.dotwid.export_video)

        # controls_box.addWidget(reset_button)
        last_controls = QHBoxLayout()
        last_controls.addWidget(self.draw_axes_checkbox)
        last_controls.addSpacerItem(QSpacerItem(2, 2, QSizePolicy.MinimumExpanding))
        last_controls.addWidget(reset_button)
        last_controls.addSpacerItem(QSpacerItem(2, 2, QSizePolicy.MinimumExpanding))
        last_controls.addWidget(export_button)
        controls_box.addRow(last_controls)

        controls_widget = QWidget(self)
        controls_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor("#b5b5b5"))
        controls_widget.setPalette(pal)
        controls_widget.setAutoFillBackground(True)
        controls_widget.setLayout(controls_box)

        layout.addWidget(controls_widget)
        self.dotwid.timer.start(100/FRAMERATE_DEF)

        # TODO toggle showing settings, change colours

    def change_framerate(self, value):
        if value == 0:
            self.dotwid.timer.stop()
        else:
            self.dotwid.timer.start(100/value)
        self.framerate_slider_val_label.setText(str(value))

    def reset_controls(self):
        self.framerate_slider.setValue(FRAMERATE_DEF)
        self.x_multiplier_slider.setValue(X_MULT_DEF)
        self.y_multiplier_slider.setValue(Y_MULT_DEF)
        self.dot_size_slider.setValue(DOT_SIZE_DEF)
        self.num_dots_slider.setValue(NUM_DOTS_DEF)
        self.angle_factor_slider.setValue(ANGLE_FACTOR_DEF)
        self.speedmult_slider.setValue(SPEED_MULT_DEF)
        self.halfmax_slider.setValue(HALFMAX_DEF)
        self.dotwid.frame_no = 1


def main():
    app = QApplication([])
    win = Halcyon()
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
