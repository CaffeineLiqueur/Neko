import sys
import threading
import keyboard  # 用于全局快捷键监听
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMetaObject, Qt
from pet import DesktopPet
from tray import TrayIcon
from config import animations
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage


# 配置大模型
SPARKAI_APP_ID = '7fa786d8'
SPARKAI_API_KEY = '56181e8d42ae8d0f0c94d91ea6f5086b'
SPARKAI_API_SECRET = 'MjFiZDU2YzFiMGMzOWUxNmQ0MzAxOWRj'
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v1.1/chat'
SPARKAI_DOMAIN = 'lite'

spark = ChatSparkLLM(
    spark_api_url=SPARKAI_URL,
    spark_app_id=SPARKAI_APP_ID,
    spark_api_key=SPARKAI_API_KEY,
    spark_api_secret=SPARKAI_API_SECRET,
    spark_llm_domain=SPARKAI_DOMAIN,
    request_timeout=30,
    streaming=True,
)

def global_hotkey_listener(pet):
    """
    全局快捷键监听线程，用于捕获 L + Enter。
    """
    while True:
        keyboard.wait('l+enter')  # 等待按下 L + Enter
        QMetaObject.invokeMethod(
            pet, "show_custom_input_dialog",
            Qt.QueuedConnection  # 确保方法在主线程中执行
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建桌宠实例
    pet = DesktopPet(animations, scale_factor=5, frame_rate=2, spark = spark)

    # 创建托盘图标实例
    tray = TrayIcon(app, pet)

    # 显示桌宠
    pet.show()

    # 初始化时让宠物说话
    pet.show_bubble("Hi！我是你的桌面宠物，叫做 Neko。用 L+Enter 和我对话吧!\n(=｀ω´=)", duration=10000, typing_speed=100)
    # pet.show_bubble("Hi!我是你的桌面", duration=5000, typing_speed=100)

    # 启动全局快捷键监听线程
    hotkey_thread = threading.Thread(target=global_hotkey_listener, args=(pet,), daemon=True)
    hotkey_thread.start()

    sys.exit(app.exec_())