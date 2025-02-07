from PySide6 import QtCore

import icons
from components.page_about import About
from components.page_homepage import Homepage
from PySide6.QtGui import QIcon, QScreen, QGuiApplication, Qt
# from PyQt5.QtWidgets import QDesktopWidget

import siui
from siui.core import SiColor, SiGlobal
from siui.templates.application.application import SiliconApplication

# 载入图标
siui.core.globals.SiGlobal.siui.loadIcons(
    icons.IconDictionary(color=SiGlobal.siui.colors.fromToken(SiColor.SVG_NORMAL)).icons
)


class MySiliconApp(SiliconApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.is_dragging = False  # 拖动标志，用于判断是否在拖动窗口
        self.drag_position = QtCore.QPoint()  # 记录拖动开始时的鼠标位置与窗口左上角的位置差

        self.setMinimumSize(1024, 380)
        self.resize(1366, 916)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 设置窗口为无边框
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)   #  窗口在任务栏上切换
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景为透明

        self.centerOnScreen()   # 让窗口居中

        # 标题栏文字
        title_text = "标题栏文字"

        # 链接函数
        self.layerMain().app_max_button.clicked.connect(self.toggleMaximized)
        self.layerMain().app_min_button.clicked.connect(self.showMinimized)
        self.layerMain().app_close_button.clicked.connect(self.close)

        self.layerMain().app_title.mouseDoubleClickEvent = self.restoreWindowSize  # 用于双击标题栏时最大化与还原
        self.layerMain().container_title.mouseDoubleClickEvent = self.restoreWindowSize  # 用于双击标题栏时最大化与还原



        self.layerMain().setTitle(title_text)
        self.layerMain()
        self.setWindowTitle(title_text)
        self.setWindowIcon(QIcon("./img/logo_new.png"))
        self.layerMain().addPage(Homepage(self),
                                 icon=SiGlobal.siui.iconpack.get("ic_fluent_home_filled"),
                                 hint="主页", side="top")

        self.layerMain().addPage(About(self),
                                 icon=SiGlobal.siui.iconpack.get("ic_fluent_info_filled"),
                                 hint="关于", side="bottom")

        self.layerMain().setPage(0)

        SiGlobal.siui.reloadAllWindowsStyleSheet()



    def toggleMaximized(self):
        """
         切换窗口的最大化状态。
         如果窗口当前处于最大化状态，则将其恢复为正常大小；
         如果窗口当前不是最大化状态，则将其最大化。
         """
        if self.isMaximized():
            self.showNormal()
            self.layerMain().app_max_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_maximize_filled"))
            self.layerMain().app_max_button.attachment().setToolTip("最大化")
            # # 最大化后可能需要调整窗口位置
            self.centerOnScreen()

        else:
            # 在最大化之前调整窗口位置，避免与任务栏重叠
            self.move(0, 0)  # 将窗口移动到左上角
            self.showMaximized()
            self.layerMain().app_max_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_minimize_filled"))
            self.layerMain().app_max_button.attachment().setToolTip("还原")


    def mousePressEvent(self, event):
        """
        鼠标按下事件处理函数。
        如果按下的是左键，并且窗口不是最大化状态，则准备拖动窗口。
        """
        if event.button() == Qt.LeftButton:
            if self.isMaximized():
                self.is_dragging = False  # 如果窗口已最大化，则不进行拖动
            else:
                self.is_dragging = True  # 设置拖动标志为True
                # 计算拖动开始时的鼠标位置与窗口左上角的位置差
                # self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        else:
            super().mousePressEvent(event)  # 如果不是左键，则调用父类的鼠标按下事件处理函数

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件处理函数。
        如果拖动标志为True，则根据鼠标的移动更新窗口的位置。
        """
        if self.is_dragging:
            # 更新窗口位置
            new_position = event.globalPosition().toPoint() - self.drag_position
            self.move(new_position)
        else:
            super().mouseMoveEvent(event)  # 如果不是拖动状态，则调用父类的鼠标移动事件处理函数



    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件处理函数。
        如果拖动标志为True，则将其设置为False，表示拖动结束。
        """
        if self.is_dragging:
            self.is_dragging = False  # 重置拖动标志
        else:
            super().mouseReleaseEvent(event)  # 如果不是拖动状态，则调用父类的鼠标释放事件处理函数


    def restoreWindowSize(self, event):
        """
        切换窗口的显示状态。

        如果窗口当前处于最大化状态，则将其还原为正常大小；
        如果窗口当前不是最大化状态，则将其最大化。

        参数:
            event (QEvent): 触发此函数的事件对象。
        """
        self.toggleMaximized()
        # 需要调用event.accept()来接受事件，否则双击事件不会被处理
        event.accept()

    def centerOnScreen(self):
        """
        计算并设置窗口的位置，使其位于屏幕的正中央。
        """

        # 获取主屏幕的尺寸
        screen = QGuiApplication.primaryScreen().size()  # 获取屏幕尺寸，返回一个QSize对象

        # 获取当前窗口的尺寸
        size = self.geometry()  # 获取窗口的几何尺寸，返回一个QRect对象

        # 计算窗口应移动到的x和y坐标，以使窗口居中
        # 宽度差的一半和高度差的一半分别作为x和y的偏移量
        x = (screen.width() - size.width()) / 2
        y = (screen.height() - size.height()) / 2

        # 使用计算出的x和y坐标移动窗口
        self.move(int(x), int(y))  # 将窗口移动到屏幕中央
