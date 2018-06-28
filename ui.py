#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, \
        QHBoxLayout, QTextEdit, QLineEdit, QTextBrowser, QProgressBar
from PyQt5.QtCore import Qt, QPoint, QRect, QBasicTimer
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QCursor
import ThreadPool
# from syn_scan import scan
from connect_scan import scan
# endTag = '`'
stopTag = True  # 一开始是stop
thread_num = 300  # 线程池的线程数


class QTitleLabel(QLabel):
    """
    新建标题栏标签类
    """
    def __init__(self, *args):
        super(QTitleLabel, self).__init__(*args)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setFixedHeight(30)


class QTitleButton(QPushButton):
    """
    新建标题栏按钮类
    """
    def __init__(self, *args):
        super(QTitleButton, self).__init__(*args)
        self.setFont(QFont("Webdings")) # 特殊字体以不借助图片实现最小化最大化和关闭按钮
        self.setFixedWidth(40)

class QUnFrameWindow(QWidget):
    """
    无边框窗口类
    """
    def __init__(self):
        super(QUnFrameWindow, self).__init__(None, Qt.FramelessWindowHint)  # 设置为顶级窗口，无边框
        # 属性
        self._padding = 5  # 设置边界宽度为5
        self.setWindowTitle = self._setTitleText(self.setWindowTitle)  # 用装饰器将设置WindowTitle名字函数共享到标题栏标签上
        self.showText = ''  # 将在 TextBrowser 上展示的信息
        # 函数
        self.initTitleLabel()  # 安放标题栏标签
        self.setWindowTitle("端口扫描")
        self.initLayout()  # 设置框架布局
        self.setMinimumWidth(250)
        self.setMinimumHeight(200)
        self.resize(500, 400)

        self.setMouseTracking(True)  # 设置widget鼠标跟踪
        self.initDrag()  # 设置鼠标跟踪判断默认值
        self.initWidgets()  # 加载主体部件
        self.setObjectName('app')

    def initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def initTitleLabel(self):
        # 安放标题栏标签
        self._TitleLabel = QTitleLabel(self)
        self._TitleLabel.setMouseTracking(True) # 设置标题栏标签鼠标跟踪（如不设，则标题栏内在widget上层，无法实现跟踪）
        self._TitleLabel.setIndent(10)  # 设置标题栏文本缩进
        self._TitleLabel.move(0, 0)  # 标题栏安放到左上角

    def initLayout(self):
        # 设置框架布局
        t = QLabel(self)
        t.setFixedHeight(20)
        self._MainLayout = QVBoxLayout()
        self._MainLayout.setSpacing(0)
        self._MainLayout.addWidget(t, Qt.AlignTop)  # 顶一个QLabel在竖放框架第一行，以免正常内容挤占到标题范围里
        # self._MainLayout.addStretch()  # 平均分配空间
        self.setLayout(self._MainLayout)

    def addLayout(self, QLayout):
        # 给widget定义一个addLayout函数，以实现往竖放框架的正确内容区内嵌套Layout框架
        self._MainLayout.addLayout(QLayout)

    def _setTitleText(self, func):
        # 设置标题栏标签的装饰器函数
        def wrapper(*args):
            self._TitleLabel.setText(*args)
            return func(*args)
        return wrapper

    def setTitleAlignment(self, alignment):
        # 给widget定义一个setTitleAlignment函数，以实现标题栏标签的对齐方式设定
        self._TitleLabel.setAlignment(alignment | Qt.AlignVCenter)

    def setCloseButton(self, bool):
        # 给widget定义一个setCloseButton函数，为True时设置一个关闭按钮
        if bool == True:
            self._CloseButton = QTitleButton(b'\xef\x81\xb2'.decode("utf-8"), self)
            self._CloseButton.setObjectName("CloseButton") # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._CloseButton.setToolTip("关闭窗口")
            self._CloseButton.setMouseTracking(True) # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._CloseButton.setFixedHeight(self._TitleLabel.height()) # 设置按钮高度为标题栏高度
            self._CloseButton.clicked.connect(self.close) # 按钮信号连接到关闭窗口的槽函数


    def setMinMaxButtons(self, bool):
        # 给widget定义一个setMinMaxButtons函数，为True时设置一组最小化最大化按钮
        if bool == True:
            self._MinimumButton = QTitleButton(b'\xef\x80\xb0'.decode("utf-8"), self)
            self._MinimumButton.setObjectName("MinMaxButton") # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._MinimumButton.setToolTip("最小化")
            self._MinimumButton.setMouseTracking(True) # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._MinimumButton.setFixedHeight(self._TitleLabel.height()) # 设置按钮高度为标题栏高度
            self._MinimumButton.clicked.connect(self.showMinimized) # 按钮信号连接到最小化窗口的槽函数
            self._MaximumButton = QTitleButton(b'\xef\x80\xb1'.decode("utf-8"), self)
            self._MaximumButton.setObjectName("MinMaxButton") # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._MaximumButton.setToolTip("最大化")
            self._MaximumButton.setMouseTracking(True) # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._MaximumButton.setFixedHeight(self._TitleLabel.height()) # 设置按钮高度为标题栏高度
            self._MaximumButton.clicked.connect(self._changeNormalButton) # 按钮信号连接切换到恢复窗口大小按钮函数

    def _changeNormalButton(self):
        # 切换到恢复窗口大小按钮
        try:
            self.showMaximized() # 先实现窗口最大化
            self._MaximumButton.setText(b'\xef\x80\xb2'.decode("utf-8")) # 更改按钮文本
            self._MaximumButton.setToolTip("恢复") # 更改按钮提示
            self._MaximumButton.disconnect() # 断开原本的信号槽连接
            self._MaximumButton.clicked.connect(self._changeMaxButton) # 重新连接信号和槽
        except:
            pass

    def _changeMaxButton(self):
        # 切换到最大化按钮
        try:
            self.showNormal()
            self._MaximumButton.setText(b'\xef\x80\xb1'.decode("utf-8"))
            self._MaximumButton.setToolTip("最大化")
            self._MaximumButton.disconnect()
            self._MaximumButton.clicked.connect(self._changeNormalButton)
        except:
            pass

    def resizeEvent(self, QResizeEvent):
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width()) # 将标题标签始终设为窗口宽度
        # 分别移动三个按钮到正确的位置
        try:
            self._CloseButton.move(self.width() - self._CloseButton.width(), 0)
        except:
            pass
        try:
            self._MinimumButton.move(self.width() - (self._CloseButton.width() + 1) * 3 + 1, 0)
        except:
            pass
        try:
            self._MaximumButton.move(self.width() - (self._CloseButton.width() + 1) * 2 + 1, 0)
        except:
            pass
        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                           for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                         for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                                    for y in range(self.height() - self._padding, self.height() + 1)]

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self._TitleLabel.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势
        if QMouseEvent.pos() in self._corner_rect:
            self.setCursor(Qt.SizeFDiagCursor)
        elif QMouseEvent.pos() in self._bottom_rect:
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._right_rect:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def initWidgets(self):
        # 主布局
        self.main_widget_layout = QVBoxLayout()
        self.addLayout(self.main_widget_layout)

        # 文本显示框
        self.textview = QTextBrowser()
        self.textview.setText('输入ip及端口信息即可开始扫描\n')
        self.textview.setObjectName('show_text')
        # 四个线性输入框
        self.line_text = [QLineEdit(self) for _ in range(4)]
        # 四个label， 分别是四个输入框前的解释
        self.text_name = [QLabel(self) for _ in range(4)]

        self.input_layout = QVBoxLayout()  # 四个输入布局
        tmp = (' 扫描起始ip:  ', ' 扫描结束ip:  ', ' 扫描起始端口:', ' 扫描结束端口:')
        for i in range(4):
            self.line_text[i].setObjectName('ip_or_port')
            self.text_name[i].setObjectName('input_tip')
            self.text_name[i].setText(tmp[i])
            liner_layout = QHBoxLayout()
            liner_layout.addWidget(self.text_name[i])
            liner_layout.addWidget(self.line_text[i])
            self.input_layout.addLayout(liner_layout)

        # 两个按键及其布局  置于底部
        self.start_btn = QPushButton('开始扫描', self)
        self.end_btn = QPushButton('结束扫描', self)
        # 绑定点击事件
        self.start_btn.clicked.connect(self.start_scan)
        self.end_btn.clicked.connect(self.stop_scan)
        self.start_btn.setShortcut('Enter')

        self.start_btn.setObjectName('start_end')
        self.end_btn.setObjectName('start_end')
        self.start_btn.setMinimumHeight(25)
        self.end_btn.setMinimumHeight(25)
        t = QLabel()
        t.setFixedSize(20, 20)  # t 用来留空
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.start_btn)
        self.btn_layout.addWidget(t)
        self.btn_layout.addWidget(self.end_btn)
        # 进度条
        self.progressBar = QProgressBar(self)
        self.progressBar.setFixedHeight(25)
        self.progress = 0  # 进度值
        self.timer = QBasicTimer()
        # self.progressBar.setValue(50)
        # 主布局分为两个，上面的是两个布局加Textedit，下面是button布局,底部进度条
        self.mid_layout = QHBoxLayout()
        self.mid_layout.addWidget(self.textview)
        self.mid_layout.addLayout(self.input_layout)
        self.main_widget_layout.addLayout(self.mid_layout)
        self.main_widget_layout.addWidget(t)
        self.main_widget_layout.addLayout(self.btn_layout)
        self.main_widget_layout.addWidget(self.progressBar)

        # Debug
        self.line_text[0].setText('192.168.0.106')
        self.line_text[1].setText('192.168.0.106')
        self.line_text[2].setText('80')
        self.line_text[3].setText('10000')

    def timerEvent(self, *args, **kwargs):
        if not stopTag and self.progress < 100:  # 未结束的时候自动跑
            self.progressBar.setValue(self.progress)
            self.progress += 1

    def calculateTime(self, startip, endip, startport, endport):
        # 前两个str，后两个int
        port_range = endport - startport + 1
        S_ip = startip.split('.')
        E_ip = endip.split('.')
        Fourth_ip_range = int(E_ip[3]) - int(S_ip[3]) + 1
        Third_ip_range = int(E_ip[2]) - int(S_ip[2]) + 1
        t = port_range * Fourth_ip_range * Third_ip_range * 1.5
        print('预计花费时间', t, '秒')
        return t

    def start_scan(self):
        print('start')
        global stopTag
        stopTag = False
        self.start_btn.setEnabled(False)
        self.end_btn.setEnabled(True)
        # 读取输入信息
        startip = self.line_text[0].text()
        endip = self.line_text[1].text()
        startport = self.line_text[2].text()
        endport = self.line_text[3].text()
        # 启动计时器，负责计算进度时间
        interval_time = self.calculateTime(startip, endip, int(startport), int(endport))  # 计算结果为秒
        self.timer.start(interval_time*10/thread_num, self)  # 每隔多少秒增加进度，传入参数为毫秒除以线程数

        scan_range = (startip, endip, startport, endport)
        self.result = []  # 结果列表
        self.textview.setText(' 开始扫描...')
        # 负责启动扫描的主线程，将很快退出
        self.work_thread = WorkThread(scan_range, self.result)
        # self.work_thread.signal_str.connect(self.handle_work)
        self.work_thread.start()
        # 检测result，更新的线程
        self.update_thread = UpdateThread(self.result)
        self.update_thread.signal_result.connect(self.handle_work)
        self.update_thread.start()

    def stop_scan(self):
        global stopTag
        stopTag = True
        self.progress = 0
        self.progressBar.setValue(self.progress)  # 重设进度
        self.timer.stop()  # 计时器停止
        self.end_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        print('stop')

    def handle_work(self, signal_str):  # 接收从线程work_thread传过来的str类型的信号参数
        # print('received:', signal_str[0:10])
        if signal_str == '':
            self.textview.setText("Don't find any open port.")
            return
        if not WorkThread.scan_thread_pool.work_queue.empty():
            self.textview.setText(signal_str + '\n' + '扫描中......')
            return
        self.textview.setText(signal_str + '\n' + '扫描完成')
        self.progressBar.setValue(100)


class WorkThread(QtCore.QThread):
    signal_str = QtCore.pyqtSignal(str)
    scan_thread_pool = ThreadPool.ThreadPoolManager(thread_num)  # 线程池

    def __init__(self, scan_range, result):
        super(WorkThread, self).__init__()
        self.scan_range = scan_range
        self.result = result

    def run(self):
        print('WorkThread is running')
        startIp = self.scan_range[0].split('.')
        endIp = self.scan_range[1].split('.')
        startPort = int(self.scan_range[2])
        endPort = int(self.scan_range[3])
        # for i in range(len(startIp)):
        #     startIp[i] = int(startIp[i])
        # for i in range(len(endIp)):
        #     endIp[i] = int(endIp[i])

        if startIp[0] != endIp[0] or startIp[1] != endIp[1]:
            self.signal_str.emit('范围区间过大，不想扫  `')
            return
        # 已知假设 startip小于等于endip ，startport小于等于endport
        s_ip2 = int(startIp[2])
        s_ip3 = int(startIp[3])
        e_ip2 = int(endIp[2])
        e_ip3 = int(endIp[3])

        for i in range(startPort, endPort+1):
            for j in range(s_ip3, e_ip3+1):
                for k in range(s_ip2, e_ip2+1):
                    if not stopTag:
                        dst_ip = startIp[0] + '.' + startIp[1] + '.' + str(k) + '.' + str(j)  # 目标ip str型
                        dst_port = i  # 目标端口 int型
                        # scan_info = (dst_ip, dst_port, open_port)
                        WorkThread.scan_thread_pool.add_job(scan, dst_ip, dst_port, self.result)
        print('WorkThread is exited')


class UpdateThread(QtCore.QThread):
    signal_result = QtCore.pyqtSignal(str)
    # signal_progress = QtCore.pyqtSignal(int)

    def __init__(self, result):
        super(UpdateThread, self).__init__()
        self.result = result

    def run(self):
        global stopTag
        current_result_num = len(self.result)
        print('update thread is running.')
        while not stopTag:
            if len(self.result) > current_result_num:
                print('add open port', self.result[-1])
                current_result_num = len(self.result)
                self.signal_result.emit('\n'.join(self.result))

            else:
                if WorkThread.scan_thread_pool.work_queue.empty():
                    # print('empty')
                    stopTag = True  # 结束
                time.sleep(0.1)

        # 取出（抢出）任务队列所有元素，结束任务
        try:
            while not WorkThread.scan_thread_pool.work_queue.empty():
                WorkThread.scan_thread_pool.work_queue.get(block=False)
        except Exception as e:
            print('\n\n----------error:', type(e), e, '----------\n\n')

        self.signal_result.emit('\n'.join(self.result))  # 再发送一次，以便修改结束标记
        print('update thread is exited.')


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet(open("./ui.qss").read())
    window = QUnFrameWindow()
    window.setCloseButton(True)
    window.setMinMaxButtons(True)
    window.show()
    sys.exit(app.exec_())
