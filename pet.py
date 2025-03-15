import random
import time
from typing import Any

from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QInputDialog, QDialog, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.uic.properties import QtCore
from sparkai.core.callbacks import BaseCallbackHandler

from input_dialog import InputDialog  # 导入新的输入框模块
import threading
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage


class BubbleChunkHandler(ChunkPrintHandler):
    """
    扩展 ChunkPrintHandler，将流式输出直接更新到桌宠气泡框中。
    """
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.current_text = ""  # 用于存储当前气泡框内容

    def on_llm_new_token(self, token: str, *, chunk: None, **kwargs: Any):
        """
        每当生成一个新 token 时调用，直接更新气泡框。
        """
        # print(token, end='')
        # print(self.current_text)
        self.current_text += token
        self.pet.update_bubble(self.current_text, duration=5000)  # 直接更新气泡框内容
        # self.bubble_timer.start(2000)

class DesktopPet(QWidget):
    def __init__(self, animations, scale_factor=2, frame_rate=10, spark=None):
        super().__init__()
        self.animations = animations  # 动画帧字典
        self.scale_factor = scale_factor
        self.frame_rate = frame_rate
        self.spark = spark  # 引入大模型接口实例
        self.current_state = "stand"
        self.previous_state = "stand"  # 用于记录切换前的状态
        self.current_frame_index = 0
        self.move_speed = 5  # 移动速度
        self.allow_movement = True  # 新增变量：是否允许移动

        # 初始化窗口
        self.init_ui()

        # 动画定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(1000 // self.frame_rate)

        # 状态切换定时器
        self.state_timer = QTimer(self)
        self.state_timer.timeout.connect(self.change_state)
        self.state_timer.start(5000)  # 每2秒随机切换状态

        # 气泡框定时器
        self.bubble_timer = QTimer(self)
        # self.bubble_timer.setSingleShot(True)  # 定时器设置为只触发一次
        self.bubble_timer.timeout.connect(self.hide_bubble)

        # 打字效果定时器
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_next_character)

    def init_ui(self):
        """
        初始化桌宠窗口设置。
        """
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint  # 窗口置顶
            | Qt.FramelessWindowHint  # 无边框
            | Qt.Tool  # 工具窗口，不显示在任务栏
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 背景透明

        # 加载站立状态的第一帧以设置窗口大小
        first_frame = QPixmap(self.animations["stand"][0])
        scaled_size = first_frame.size() * self.scale_factor
        self.setFixedSize(scaled_size)

        # 添加 QLabel 显示图片
        self.label = QLabel(self)
        self.label.setFixedSize(self.size())
        self.label.setScaledContents(False)

        # 设置初始位置（右下角偏上）
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width, screen_height = screen_geometry.width(), screen_geometry.height()
        pet_width, pet_height = self.width(), self.height()
        offset_x, offset_y = 20, 50  # 偏移量，避免完全贴在右下角
        initial_x = screen_width - pet_width - offset_x
        initial_y = screen_height - pet_height - offset_y
        self.move(initial_x, initial_y)

        # 创建气泡框
        self.bubble_label = QLabel(self)
        self.bubble_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.9);  /* 半透明白色背景 */
            border: 2px solid #4CAF50;  /* 绿色边框 */
            border-radius: 15px;       /* 圆角 */
            padding: 10px;             /* 内边距 */
            font-size: 14px;           /* 字体大小 */
            color: black;              /* 字体颜色 */   
        """)
        font = QFont("Microsoft YaHei", 14)  # 微软雅黑，大小12
        font.setBold(True)  # 可设置是否加粗

        self.bubble_label.setFont(font)
        self.bubble_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.bubble_label.setWordWrap(True)
        self.bubble_label.setVisible(False)
        self.bubble_label.resize(200, 100)

        # 显示第一帧
        self.update_frame()

    @pyqtSlot()
    def show_custom_input_dialog(self):
        """
        弹出自定义输入框，与宠物对话。
        """
        input_dialog = InputDialog(self, self.handle_input)
        pet_x, pet_y = self.x(), self.y()
        pet_width, pet_height = self.width(), self.height()
        dialog_x = pet_x + (pet_width - input_dialog.width()) // 2  # 水平居中
        dialog_y = pet_y + pet_height - 15 * self.scale_factor  # 紧贴宠物下方，留10像素间距
        input_dialog.move(dialog_x, dialog_y)
        input_dialog.exec_()

    def handle_input(self, dialog, text):
        """
        处理输入框中的文字，并与宠物对话。
        """
        dialog.close()
        if text.strip():
            threading.Thread(target=self.fetch_response, args=(text,), daemon=True).start()

    def fetch_response(self, user_input):
        """
        调用大模型接口并逐字显示响应。
        """
        try:
            messages = [
                # ChatMessage(
                #     role="assistant", content='我现在正在扮演一个非常可爱的小猫机器人，名字叫做Neko。我会用很可爱的话和你沟通的。'
                # ),
                ChatMessage(
                    role="user", content='你现在正在扮演一个非常可爱的小猫机器人，名字叫做Neko。你要用很可爱的话和我沟通。但是不要发出喵的声音。'
                ),
                ChatMessage(role="user", content=user_input)
            ]
            handler = BubbleChunkHandler(self)  # 使用 BubbleChunkHandler
            a = self.spark.generate([messages], callbacks=[handler])  # 调用大模型生成
            time.sleep(5)
            self.hide_bubble()
            # print(a.generations[0][0].text)
            # self.show_bubble('a.generations[0][0].text', duration=5000, typing_speed=100)
        except Exception as e:
            self.update_bubble(f"错误: {str(e)}")  # 显示错误信息

    def next_frame(self):
        """
        切换到当前状态的下一帧图片。
        """
        frames = self.animations[self.current_state]
        self.current_frame_index = (self.current_frame_index + 1) % len(frames)
        self.update_frame()

        # 更新位置（随机移动）
        if self.current_state in ["walk_left", "walk_right", "walk_up", "walk_down"]:
            self.update_position()

    def update_frame(self):
        """
        更新当前帧并按比例无锯齿放大。
        """
        # print('现在的状态：', self.current_state)
        frame_path = self.animations[self.current_state][self.current_frame_index]
        pixmap = QPixmap(frame_path)
        scaled_pixmap = pixmap.scaled(
            self.width(), self.height(),
            # Qt.KeepAspectRatio,
            # Qt.SmoothTransformation  # 高质量插值，减少锯齿
        )
        self.label.setPixmap(scaled_pixmap)

    def change_state(self):
        """
        随机切换桌宠状态。
        """
        # 如果当前处于拖拽状态，不切换
        if self.current_state == "dragged" or not self.allow_movement:
            return

        self.current_state = random.choice(['stand', 'walk_left', 'walk_right', 'walk_up', 'walk_down'])
        self.current_frame_index = 0  # 切换状态后从第一帧开始

    def update_position(self):
        """
        根据状态更新桌宠的位置。
        """
        x, y = self.x(), self.y()
        if self.current_state == "walk_left":
            x -= self.move_speed
        elif self.current_state == "walk_right":
            x += self.move_speed
        elif self.current_state == "walk_up":
            y -= self.move_speed
        elif self.current_state == "walk_down":
            y += self.move_speed

        # 屏幕边界检测
        screen_geometry = QApplication.desktop().screenGeometry()
        x = max(0, min(x, screen_geometry.width() - self.width()))
        y = max(0, min(y, screen_geometry.height() - self.height()))

        self.move(x, y)

    def update_bubble(self, text, duration=3000):
        """
        更新气泡框内容。
        """
        self.bubble_label.setVisible(True)  # 确保气泡框可见
        self.bubble_label.setText(text)  # 更新气泡框的文字内容

        # 自动调整气泡框大小
        max_width = 200
        self.bubble_label.setWordWrap(True)
        self.bubble_label.setFixedWidth(max_width)
        metrics = self.bubble_label.fontMetrics()
        lines = metrics.boundingRect(0, 0, max_width, 0, Qt.TextWordWrap, text)
        self.bubble_label.resize(lines.width() + 20, lines.height() + 50)

        # 将气泡框位置调整到宠物窗口上方
        self.bubble_label.move(
            self.width() // 2 - self.bubble_label.width() // 2,  # 水平居中
            0  # 在窗口上方显示
        )
        # # 重置并启动定时器
        # if self.bubble_timer.isActive():  # 如果定时器已经在运行，先停止
        #     self.bubble_timer.stop()
        # self.bubble_timer.start(duration)  # 设置新的隐藏时间

    def show_bubble(self, text, duration=3000, typing_speed=50):
        """
        显示气泡框并逐字输出文本。
        """
        self.bubble_label.setText("")  # 清空当前显示内容
        self.bubble_label.setVisible(True)  # 确保气泡框可见

        # 设置气泡框最大宽度（自动换行）
        max_width = 200
        self.bubble_label.setWordWrap(True)
        self.bubble_label.setFixedWidth(max_width)

        # 使用 fontMetrics 自动计算大小
        metrics = self.bubble_label.fontMetrics()
        lines = metrics.boundingRect(0, 0, max_width, 0, Qt.TextWordWrap, text)
        self.bubble_label.resize(lines.width() + 20, lines.height() + 50)
        # print(self.height())
        # print(self.bubble_label.height())
        # 将气泡框移动到宠物窗口上方
        self.bubble_label.move(
            self.width() // 2 - self.bubble_label.width() // 2,  # 水平居中
            0  # 在窗口上方显示
            # self.y() - self.height() - 32 * self.scale_factor
        )

        # 保存文字和逐字输出相关变量
        self.full_text = text
        self.current_text = ""
        self.typing_index = 0

        # 启动打字效果定时器
        self.typing_timer.start(typing_speed)

        # 设置自动隐藏定时器
        self.bubble_timer.start(duration)
        # print(f"Bubble position: {self.bubble_label.pos()}")

    def type_next_character(self):
        """
        逐字输出文字内容。
        """
        # print(f"Bubble position: {self.bubble_label.pos()}")
        if self.typing_index < len(self.full_text):
            self.current_text += self.full_text[self.typing_index]
            self.bubble_label.setText(self.current_text)
            self.typing_index += 1
        else:
            # 停止打字效果
            self.typing_timer.stop()

    def hide_bubble(self):
        """
        隐藏气泡框。
        """
        self.bubble_label.setVisible(False)
        self.bubble_timer.stop()
        print('隐藏！')

    def mousePressEvent(self, event):
        """
        实现拖动功能：记录鼠标按下位置并切换到拖拽状态。
        """
        if event.button() == Qt.LeftButton:
            self.previous_state = self.current_state  # 记录当前状态
            self.current_state = "dragged"  # 切换到拖拽状态
            self.current_frame_index = 0  # 重置动画帧索引
            self.mouse_drag_position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        实现拖动功能：跟随鼠标移动。
        """
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.mouse_drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        恢复到之前的状态。
        """
        if event.button() == Qt.LeftButton:
            self.current_state = self.previous_state
            self.current_frame_index = 0  # 重置动画帧索引
            event.accept()

    def set_allow_movement(self, allow):
        """
        设置是否允许移动。
        """
        self.allow_movement = allow
        if not allow:
            # 立即切换到 stand 状态
            self.current_state = "stand"
            self.current_frame_index = 0