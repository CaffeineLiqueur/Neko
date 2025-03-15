from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

class TrayIcon:
    def __init__(self, app, pet):
        """
        初始化托盘图标。
        :param app: QApplication 实例
        :param pet: DesktopPet 实例
        """
        self.app = app
        self.pet = pet
        self.tray_icon = QSystemTrayIcon(QIcon("resources/icon.png"), self.app)

        # 创建托盘菜单
        self.create_tray_menu()

    def create_tray_menu(self):
        """
        创建托盘菜单。
        """
        menu = QMenu()

        # 创建菜单项
        show_action = QAction("显示桌宠", self.app)
        hide_action = QAction("隐藏桌宠", self.app)
        stop_movement_action = QAction("停止移动", self.app, checkable=True)
        exit_action = QAction("退出", self.app)

        # 绑定动作
        show_action.triggered.connect(self.pet.show)
        hide_action.triggered.connect(self.pet.hide)
        stop_movement_action.triggered.connect(self.toggle_movement)
        exit_action.triggered.connect(self.exit_app)


        # 添加菜单项
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addAction(stop_movement_action)
        menu.addSeparator()
        menu.addAction(exit_action)


        # 设置托盘菜单
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def exit_app(self):
        """
        退出应用程序。
        """
        self.pet.close()
        self.tray_icon.hide()
        self.app.quit()

    def toggle_movement(self, checked):
        """
        切换宠物是否允许移动。
        """
        self.pet.set_allow_movement(not checked)  # 如果选中“停止移动”，则禁用移动