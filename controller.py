# controller.py
# this program manages the GUI of the controller
# June 2019: Sinclair Gurny


# Get video module
import video_controller as vcon
# PyQt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# misc modules
import socket, threading, time, sys

class Program(QWidget):
    default_horz = 116
    default_vert = 68

    def __init__(self):
        super(Program, self).__init__()
        # Robot connections
        self.ctrl_con = None
        self.robo_vis = None
        # Buttons
        self.f = QPushButton(self)
        self.b = QPushButton(self)
        self.l = QPushButton(self)
        self.r = QPushButton(self)
        self.s1 = QPushButton(self)
        self.s2 = QPushButton(self)
        self.con = QPushButton(self)
        self.tsend = QPushButton(self)
        self.led = QPushButton(self)
        self.h_reset = QPushButton(self)
        self.v_reset = QPushButton(self)
        self.s_reset = QPushButton(self)
        # Face Recognition
        self.is_face_recog_on = False
        self.is_ar_on = False
        self.face_button = QPushButton(self)
        self.face_save = QPushButton(self)
        self.face_recog_status = QLabel(self)
        self.ar_mode = QPushButton(self)
        # Recording
        self.is_recording_vid = False
        self.record_pic1 = QPushButton(self)
        self.record_pic2 = QPushButton(self)
        self.record_vid = QPushButton(self)
        # Custom command
        self.textbox = QLineEdit(self)
        # Sliders
        self.speed_label = QLabel(self)
        self.speed_num = QLCDNumber(self)
        self.h_label = QLabel(self)
        self.h_num = QLCDNumber(self)
        self.v_label = QLabel(self)
        self.v_num = QLCDNumber(self)
        self.speed = QSlider(Qt.Horizontal, self)
        self.h_slider = QSlider(Qt.Horizontal, self)
        self.v_slider = QSlider(Qt.Horizontal, self)
        # Indicator
        self.is_con = QLabel(self)
        self.is_con_status = False
        # Video Screen
        self.screen = QLabel(self)
        self.frame = QFrame(self)
        # Continue init
        self.lcdSetup()
        self.sliderSetup()
        self.connectButtons()
        self.initializeUI()

    def initializeUI(self):
        # Set text
        self.f.setText(u"\u2191")
        self.b.setText(u"\u2193")
        self.l.setText(u"\u2190")
        self.r.setText(u"\u2192")
        self.s1.setText('STOP')
        self.s2.setText('STOP')
        self.con.setText("Connect")
        self.led.setText('LED')
        self.s_reset.setText('Reset')
        self.h_reset.setText('Reset')
        self.v_reset.setText('Reset')
        self.speed_label.setText('Driving Speed:')
        self.h_label.setText('Horizontal Camera:')
        self.v_label.setText('Vertical Camera:')
        self.record_pic1.setText('Save Clean Screenshot')
        self.record_pic2.setText('Save Screenshot')
        self.record_vid.setText('Start Recording')
        self.ar_mode.setText('AR MODE OFF')
        # Setup Window
        self.setGeometry(700,200,940,550)
        self.setWindowTitle("Robot Controller")
        # Place Buttons
        self.f.move(70,50); self.b.move(70,110)
        self.l.move(20,80); self.r.move(120,80)
        self.con.move(20,10); self.led.move(170, 110)
        self.s1.move(170, 50); self.s2.move(120, 510)
        self.record_pic1.move(545, 10); self.record_pic2.move(700, 10)
        self.record_vid.move(815, 10)
        # Face Recognition
        self.face_recog_status.setText("Status: OFF")
        self.face_button.setText('Toggle Face Recognition')
        self.face_save.setText('Remember Faces')
        self.face_button.move(20, 400)
        self.face_save.move(20, 430)
        self.face_recog_status.move(185, 405)
        self.ar_mode.move(150, 430)
        # Sliders
        self.speed_label.move(20,155)
        self.s_reset.move(195,150)
        self.speed_num.move(210,180)
        self.speed.setGeometry(20,185,180,30)
        self.h_label.move(20,240)
        self.h_reset.move(195,235)
        self.h_num.move(210,265)
        self.h_slider.setGeometry(20,270,180,30)
        self.v_label.move(20,325)
        self.v_reset.move(195,320)
        self.v_num.move(210,350)
        self.v_slider.setGeometry(20,355,180,30)
        # Text box
        self.textbox.move(20,470)
        self.textbox.resize(220,30)
        self.tsend.setText('Send')
        self.tsend.move(20, 510)
        # Video label
        self.screen.move(280,50)
        self.screen.resize(640,480)
        self.frame.move(280,50)
        self.frame.resize(640,480)
        self.frame.setStyleSheet('background-color: rgba(0,0,0,100%)')
        # Connection status
        self.is_con.setText('Status: Disconnected')
        self.is_con.move(280, 10)
        # Show
        self.show()
        # Connect Video
        self.initializeVideo()
        # Connect Controller
        self.initializeControl()

    def initializeControl(self):
        # create socket
        self.ctrl_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ctrl_con.settimeout(0.1)
        # bind sock to port
        robo_ctrl_add = ('192.168.1.1', 2001)
        try:
            self.ctrl_con.connect(robo_ctrl_add)
            self.is_con.setText('Status: Connected')
            self.is_con_status = True
        except Exception as e:
            print(e)
            print("Could not connect to control socket")
            self.is_con.setText('Status: Disconnected')
            self.is_con_status = False

    def initializeVideo(self):
        self.th = vcon.VThread()
        self.th.changePixmap.connect(self.setImage)
        self.th.videoReady.connect(self.vReady)
        self.th.start()

    def setImage(self, image):
        self.screen.setPixmap(QPixmap.fromImage(image))

    def vReady(self, sig):
        self.frame.setStyleSheet('background-color: rgba(0,0,0,0%)')

    def connectButtons(self):
        self.f.pressed.connect(self.forward_p)
        self.f.released.connect(self.dir_stop)
        self.b.pressed.connect(self.back_p)
        self.b.released.connect(self.dir_stop)
        self.l.pressed.connect(self.left_p)
        self.l.released.connect(self.dir_stop)
        self.r.pressed.connect(self.right_p)
        self.r.released.connect(self.dir_stop)
        self.con.clicked.connect(self.reconnect)
        self.s1.clicked.connect(self.dir_stop)
        self.s2.clicked.connect(self.dir_stop)
        self.tsend.clicked.connect(self.text_send)
        self.h_reset.clicked.connect(self.reset_horz)
        self.v_reset.clicked.connect(self.reset_vert)
        self.s_reset.clicked.connect(self.reset_speed)
        self.led.pressed.connect(self.led_on)
        self.led.released.connect(self.led_off)
        self.face_button.clicked.connect(self.toggleFace)
        self.face_save.pressed.connect(self.saveFaceOn)
        self.face_save.released.connect(self.saveFaceOff)
        self.record_pic1.pressed.connect(self.saveScreenshotStart1)
        self.record_pic1.released.connect(self.saveScreenshotStop1)
        self.record_pic2.pressed.connect(self.saveScreenshotStart2)
        self.record_pic2.released.connect(self.saveScreenshotStop2)
        self.record_vid.clicked.connect(self.toggleRecord)
        self.ar_mode.clicked.connect(self.toggleAR)

    def sliderSetup(self):
        self.h_slider.setMinimum(0)
        self.h_slider.setMaximum(180)
        self.h_slider.setValue(self.default_horz)
        self.h_num.display(self.default_horz)
        self.v_slider.setMinimum(0)
        self.v_slider.setMaximum(180)
        self.v_slider.setValue(self.default_vert)
        self.v_num.display(self.default_vert)
        self.speed.setMinimum(0)
        self.speed.setMaximum(100)
        self.speed.setValue(100)
        self.speed_num.display(100)
        # Connect
        self.h_slider.valueChanged.connect(self.set_horz)
        self.v_slider.valueChanged.connect(self.set_vert)
        self.speed.valueChanged.connect(self.set_speed)

    def lcdSetup(self):
        self.speed_num.setSegmentStyle(QLCDNumber.Flat)
        self.speed_num.setMinimumHeight(40)
        self.speed_num.setMinimumWidth(40)
        self.h_num.setSegmentStyle(QLCDNumber.Flat)
        self.h_num.setMinimumHeight(40)
        self.h_num.setMinimumWidth(40)
        self.v_num.setSegmentStyle(QLCDNumber.Flat)
        self.v_num.setMinimumHeight(40)
        self.v_num.setMinimumWidth(40)

    def toggleFace(self):
        if self.is_face_recog_on:
            self.is_face_recog_on = False
            self.face_recog_status.setText("Status: OFF")
            self.th.do_face_recog = False
        else:
            self.is_face_recog_on = True
            self.face_recog_status.setText("Status: ON")
            self.th.do_face_recog = True
            
    def toggleAR(self):
        if self.is_ar_on:
            self.is_ar_on = False
            self.ar_mode.setText('AR MODE OFF')
            self.th.do_aruco = False
        else:
            self.is_ar_on = True
            self.ar_mode.setText('AR MODE ON')
            self.th.do_aruco = True

    def saveFaceOn(self):
        print("save face!!")
        self.th.save_face = True

    def saveFaceOff(self):
        self.th.save_face = False

    def toggleRecord(self):
        if self.is_recording_vid:
            self.record_vid.setText('Start Recording')
            self.is_recording_vid = False
            self.th.should_record_video = False
        else:
            self.record_vid.setText('Stop Recording')
            self.is_recording_vid = True
            self.th.should_record_video = True


    def saveScreenshotStart1(self):
        self.th.should_save_screenshot1 = True

    def saveScreenshotStop1(self):
        self.th.should_save_screenshot1 = False

    def saveScreenshotStart2(self):
        self.th.should_save_screenshot2 = True

    def saveScreenshotStop2(self):
        self.th.should_save_screenshot2 = False

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        # WASD control
        if e.key() == Qt.Key_W:
            print("forward")
            self.run_cmd( 'ff000100ff' )
        elif e.key() == Qt.Key_S:
            print("backward")
            self.run_cmd( 'ff000200ff' )
        elif e.key() == Qt.Key_A:
            print("left")
            self.run_cmd( 'ff000400ff' )
        elif e.key() == Qt.Key_D:
            print("right")
            self.run_cmd( 'ff000300ff' )
        elif e.key() == Qt.Key_Space:
            print("STOP")
            self.run_cmd( 'ff000000ff' )


    def keyReleaseEvent(self, e):
        # WASD Control
        if e.key() == Qt.Key_W or e.key() == Qt.Key_S or\
           e.key() == Qt.Key_A or e.key() == Qt.Key_D:
            print("stop")
            self.run_cmd( 'ff000000ff' )

    def reconnect(self):
        print("Reconnecting")
        self.initializeVideo()
        self.initializeControl()

    def forward_p(self):
        print("Forward")
        self.run_cmd( 'ff000100ff' )

    def back_p(self):
        print("Back")
        self.run_cmd( 'ff000200ff' )

    def left_p(self):
        print("Left")
        self.run_cmd( 'ff000400ff' )

    def right_p(self):
        print("Right")
        self.run_cmd( 'ff000300ff' )

    def dir_stop(self):
        print("Button Stop")
        self.run_cmd( 'ff000000ff' )

    def text_send(self):
        textboxValue = self.textbox.text()
        self.textbox.setText('')
        self.run_cmd( textboxValue )

    def led_on(self):
        print('LED on')
        self.run_cmd( 'ff040000ff' )

    def led_off(self):
        print('LED off')
        self.run_cmd( 'ff040100ff' )

    def set_speed(self, value):
        self.speed_num.display(value)
        h = self.num_to_hex(value)
        cmd_l = 'ff0201'+h+'ff'
        cmd_r = 'ff0202'+h+'ff'
        self.run_cmd( cmd_l )
        self.run_cmd( cmd_r )

    def set_horz(self, value):
        self.h_num.display(value)
        h = self.num_to_hex(value)
        cmd = 'ff0107'+h+'ff'
        self.run_cmd( cmd )

    def set_vert(self, value):
        self.v_num.display(value)
        h = self.num_to_hex(value)
        cmd = 'ff0108'+h+'ff'
        self.run_cmd( cmd )

    def reset_speed(self):
        self.speed.setValue(100)
        self.set_speed(100)

    def reset_horz(self):
        print('Horz reset')
        self.h_slider.setValue(self.default_horz)
        self.set_horz(self.default_horz)

    def reset_vert(self):
        print('Vert reset')
        self.v_slider.setValue(self.default_vert)
        self.set_vert(self.default_vert)

    def num_to_hex(self, num):
        if num < 10:
            return '0'+format(num,'x')
        else:
            return format(num,'x')

    def run_cmd(self, cmd_str):
        if self.is_con_status:
            byte_cmd = bytes.fromhex(cmd_str)
            self.ctrl_con.sendall( byte_cmd )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    e = Program()
    sys.exit(app.exec_())
