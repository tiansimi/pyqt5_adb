# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.py'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


import os
import subprocess
import sys
import time
from functools import partial

from PyQt5.QtCore import QThread, pyqtSignal

from untitled import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
import re
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QColor
from PyQt5.QtCore import QTimer, QTime


# class Path(Ui_MainWindow, QMainWindow):
#     def __init__(self, parent=None):
#         super(Path, self).__init__(parent)
#         self.setupUi(self)
#
#         self.path = ''
#
#     def get_file_path(self):
#         # self.path = self.label_3.text()
#         return 'adb install -r -t -d -f ' + f'{str(self.path)}'

def str_filter(res: str):
    # devices_message = res.replace(r'\r', '').replace(r'\n', '').replace(r'\t', '')
    devices_message = re.findall(r'1.+5555', res)
    return str(devices_message)


def cmd_pull(cmd):
    # output = subprocess.check_output(cmd, shell=True)
    ret = os.system(cmd)
    return ret


def create_log_dir():
    if not os.path.exists(r'D:\log'):
        os.mkdir(r'D:\log')


class Data_file:
    # 抓取目录下的一条日志
    cmd_one = 'adb pull /data/media/awlog/logcat/logcat -a D:/log'
    # 抓取所有日志
    cmd_all = 'adb pull /data/media/awlog/logcat -a  D:/log'
    cmds = 'adb logcat > D:/log.txt'
    cmd_karnel = ''  # 拉取karnel日志
    cmd_light = 'adb shell input keyevent 224'    # 亮屏操作
    cmd_reboot = 'adb reboot'    # 重启


class Ccreen_Thread(QThread):
    # 自定义信号声明
    # 使用自定义信号和UI主线程通讯，参数是发送信号时附带参数的数据类型，可以是str、int、list等
    screenSignal = pyqtSignal(str)

    # 带一个参数t
    def __init__(self, t, parent=None):
        super(Ccreen_Thread, self).__init__(parent)
        self.t = t

    # run函数是子线程中的操作，线程启动后开始执行
    def run(self):
        # 发射自定义信号
        # 通过emit函数将参数i传递给主线程，触发自定义信号
        self.screenSignal.emit(str(self.t))  # 注意这里与_signal = pyqtSignal(str)中的类型相同


class MainWindows(Ui_MainWindow, QMainWindow, Data_file):

    def __init__(self, parent=None):
        super(MainWindows, self).__init__(parent)
        self.setupUi(self)
        self.registerEvent()
        self.connect_devices()
        self.start_timer()

    def registerEvent(self):
        self.pushButton.clicked.connect(self.connect_devices)
        self.pushButton_3.clicked.connect(self.disconnect_devices)
        self.pushButton_4.clicked.connect(self.look_devices)
        self.pushButton_7.clicked.connect(self.start_screen)
        self.pushButton_5.clicked.connect(partial(self.start_cmd, Data_file.cmd_one))
        self.pushButton_6.clicked.connect(partial(self.start_cmd, Data_file.cmd_all))   # 拉取内核 日志
        self.pushButton_8.clicked.connect(partial(self.start_cmd, Data_file.cmd_light))
        self.pushButton_9.clicked.connect(partial(self.start_cmd, Data_file.cmd_reboot))
        self.pushButton_15.clicked.connect(self.install_path)
        self.pushButton_11.clicked.connect(self.start_install)


    def connect_devices(self):
        """ 连接设备 """
        cmd_str = self.lineEdit.text()
        print(cmd_str)
        cmd = 'adb connect '
        print(cmd + cmd_str)
        output = ''
        devices_mes = ''
        if cmd_str:
            output = subprocess.check_output(cmd + cmd_str, shell=True)
            devices_mes = str_filter(str(output))
            print(output)
            if 'not' not in str(output) and output:
                # self.textEdit.setPlainText(str(output))
                self.showMessage(devices_mes)
            else:
                # self.textEdit.setPlainText(' ')
                self.showMessage('连接失败，请检测ip地址或者设备状态')

    def disconnect_devices(self):
        """ 断开连接 """
        cmd_str = self.lineEdit.text()
        cmd = 'adb disconnect '
        if cmd_str:
            output = subprocess.check_output(cmd, shell=True)

    def look_devices(self):
        """ 查看连接设备 """
        cmd = 'adb devices'
        if cmd:
            print(cmd)
            self.lineEdit_2.clear()
            output = subprocess.check_output(cmd, shell=True)
            devices_msg = str_filter(str(output))
            print(devices_msg)
            self.lineEdit_2.setText(devices_msg)

    def showMessage(self, mesg):
        """ 弹窗显示连接结果 """
        self.reply = QMessageBox(QMessageBox.Information, "result", mesg)
        # 添加自定义按钮
        self.reply.addButton('确定', QMessageBox.YesRole)
        self.reply.show()

    def showMessage_question(self):
        """ 弹窗显示连接结果 """
        QMessageBox.question(self, 'ni quedm', QMessageBox.Yes|QMessageBox.No)

    def cmd_pull_button(self, cmd_lines):
        create_log_dir()
        print(cmd_lines)
        if cmd_pull(cmd=cmd_lines):
            self.showMessage('命令执行成功^_^')
        else:
            self.showMessage('命令执行失败^_^')

    def take_screenshot(self, path='D:/log/screenshot.png'):
        """adb截取手机屏幕的函数 [path]为存储路径"""
        create_log_dir()
        os.system('adb shell screencap -p >' + path)
        """安卓底层是linux,Linux的换行符是\r\n,但是Windows的换行符是\n，所以需要replace替换一下"""
        with open(path, 'rb') as f:
            data = f.read().replace(b'\r\n', b'\n')
        with open(path, 'wb') as f:
            f.write(data)
        time.sleep(0.5)
        self.showMessage('正在截屏，请稍后去到D盘log文件夹下去查看哦！')

    def start_screen(self):
        path = r'D:/log/screenshot.png'
        self.thread = Ccreen_Thread(path)
        self.thread.screenSignal.connect(self.take_screenshot)
        self.thread.start()

    def start_timer(self):
        """ 启动定时器 """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.set_end_time(18, 0)  # 设置下班时间为18:00
        self.set_booking_time(16, 0)
        self.timer.start(1000)

    def set_booking_time(self, hour, minute):
        self.booking_time = QTime(hour, minute)

    def set_end_time(self, hour, minute):
        self.end_time = QTime(hour, minute)

    def update_time(self):
        current_time = QTime.currentTime()
        if current_time >= self.end_time:
            self.label_2.setText('下班啦^_^！')
        else:
            #  = self.end_time.secsTo(current_time)
            remaining_time = current_time.secsTo(self.end_time)
            remaining_time_str = '{:02}:{:02}:{:02}'.format(
                remaining_time // 3600, (remaining_time % 3600) // 60, (remaining_time % 3600) % 60)
            self.label_2.setText('距离下班: {}'.format(remaining_time_str))
        # booking_time = self.set_booking_time(15, 49)
        # if current_time.toString() == self.booking_time.toString():
        #     self.showMessage('快订票哇！！！！')

    def start_cmd(self, path=Data_file.cmd_one):
        self.thread = Ccreen_Thread(path)
        self.thread.screenSignal.connect(self.cmd_pull_button)
        self.thread.start()

    def start_install(self):
        path = self.label_3.text()
        install_path = 'adb install -r -t -d -f ' + f'{str(path)}'
        self.thread = Ccreen_Thread(install_path)
        self.thread.screenSignal.connect(self.cmd_pull_button)
        self.thread.start()


    def install_path(self):
        fileName = QFileDialog.getOpenFileName(None, "选取文件", "./", "All Files (*);;Text Files (*.txt)")
        self.label_3.setText(str(fileName[0]))
        self.path = self.label_3.setText(str(fileName[0]))
        print(fileName)


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    App = QApplication(sys.argv)  # 创建QApplication对象，作为GUI主程序入口
    mainUi = MainWindows()
    mainUi.show()
    palette = QPalette()
    palette.setColor(QPalette.Background, QColor(0, 0, 255, 127))  # 设置窗口关键背景颜色
    palette.setBrush(QPalette.Background, QBrush(QPixmap("./IMG_5807.PNG")))  # 设置窗口关键背景图片
    mainUi.setPalette(palette)
    App.exit()
    sys.exit(App.exec_())  # 循环中等待退出程序
