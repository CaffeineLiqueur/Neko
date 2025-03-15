from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel


class Bubble(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置气泡框样式
        self.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.9);
            border: 2px solid #4CAF50;
            border-radius: 15px;
            padding: 10px;
            font-size: 14px;
            color: black;
        """)
        font = QFont("Microsoft YaHei", 14)
        font.setBold(True)
        self.setFont(font)

        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setWordWrap(True)
        self.setVisible(False)

        # 定时器
        self.typing_timer = QTimer(self)
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self.hide_bubble)
        self.typing_timer.timeout.connect(self.type_next_character)

        # 打字相关变量
        self.full_text = ""
        self.current_text = ""
        self.typing_index = 0

    def show_bubble(self, text, duration=3000, typing_speed=50):
        """
        显示气泡框并逐字输出文本。
        """
        self.setText("")
        self.setVisible(True)

        # 自动调整大小
        max_width = 200
        self.setFixedWidth(max_width)
        metrics = self.fontMetrics()
        rect = metrics.boundingRect(0, 0, max_width, 0, Qt.TextWordWrap, text)
        self.resize(rect.width() + 20, rect.height() + 20)

        # 设置文字
        self.full_text = text
        self.current_text = ""
        self.typing_index = 0

        # 启动打字效果
        self.typing_timer.start(typing_speed)
        self.hide_timer.start(duration)

    def type_next_character(self):
        """
        逐字显示文字。
        """
        if self.typing_index < len(self.full_text):
            self.current_text += self.full_text[self.typing_index]
            self.setText(self.current_text)
            self.typing_index += 1
        else:
            self.typing_timer.stop()

    def hide_bubble(self):
        """
        隐藏气泡框。
        """
        self.setVisible(False)
        self.hide_timer.stop()
        self.typing_timer.stop()
