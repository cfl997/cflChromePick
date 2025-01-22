import os
import sys
import configparser
import threading
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTimeEdit
from PyQt5.QtCore import QTime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import schedule


# 获取当前脚本目录
def get_current_dir():
    if getattr(sys, 'frozen', False):  # 检测是否为 PyInstaller 打包后的环境
        return os.path.dirname(sys.executable)  # 设置工作目录为 exe 文件所在目录
    else:
        return os.path.dirname(os.path.abspath(__file__))  # 开发环境下设置为脚本目录


# 获取当前脚本目录
#CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_DIR = get_current_dir()
DEFAULT_USER_DATA_DIR = os.path.join(CURRENT_DIR, "UserData")
CONFIG_PATH = os.path.join(CURRENT_DIR, "ChromePickconfig.ini")
LOG_PATH = os.path.join(CURRENT_DIR, "ChromePick.log")

# 配置日志
def setup_logging():
    # 设置日志记录的格式和级别
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别为 INFO
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # 控制台输出
            logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")  # 文件输出
        ]
    )

# 配置文件读取和写入操作
def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        return {
            "url1": "",
            "url2": "",
            "href": "",
            "driver_path": "",
            "user_data_dir": DEFAULT_USER_DATA_DIR,
            "time": QTime.currentTime().toString("HH:mm"),
        }
    config.read(CONFIG_PATH, encoding="utf-8")
    return {
        "url1": config.get("SETTINGS", "url1", fallback=""),
        "url2": config.get("SETTINGS", "url2", fallback=""),
        "href": config.get("SETTINGS", "href", fallback=""),
        "driver_path": config.get("SETTINGS", "driver_path", fallback=""),
        "user_data_dir": config.get("SETTINGS", "user_data_dir", fallback=DEFAULT_USER_DATA_DIR),
        "time": config.get("SETTINGS", "time", fallback=QTime.currentTime().toString("HH:mm")),
    }

def save_config(data):
    config = configparser.ConfigParser()
    config["SETTINGS"] = data
    with open(CONFIG_PATH, "w", encoding="utf-8") as configfile:
        config.write(configfile)

def open_and_click_by_href(url, href_value, driver_path, user_data_dir):
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chrome_options.add_argument("--profile-directory=Default")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        logging.info(f"打开网页: {url}")
        time.sleep(30)
        logging.info(f"等待 30 秒后开始查找按钮...")
        while True:
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[@href='{href_value}']"))
                ).click()
                #logging.info(f"成功点击 href='{href_value}' 的按钮 on {url}")
                time.sleep(15)
                logging.info(f"成功点击 href='{href_value}' 的按钮 on {url}  等待15秒后关闭...")
                break
            except Exception:
                logging.warning(f"{url} 未找到 href='{href_value}' 的按钮，30 秒后刷新重试...")
                time.sleep(30)
                driver.refresh()
    except Exception as e:
        logging.error(f"操作失败：{e}")
    finally:
        driver.quit()

class SchedulerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('定时网页点击器')
        self.resize(600, 300)

        layout = QVBoxLayout()

        time_layout = QHBoxLayout()
        time_label = QLabel('每天执行时间:')
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat('HH:mm')
        self.time_edit.setTime(QTime.fromString(self.config["time"], "HH:mm"))
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        layout.addLayout(time_layout)

        url1_layout = QHBoxLayout()
        url1_label = QLabel('网页链接 1:')
        self.url1_edit = QLineEdit(self.config["url1"])
        url1_layout.addWidget(url1_label)
        url1_layout.addWidget(self.url1_edit)
        layout.addLayout(url1_layout)

        url2_layout = QHBoxLayout()
        url2_label = QLabel('网页链接 2:')
        self.url2_edit = QLineEdit(self.config["url2"])
        url2_layout.addWidget(url2_label)
        url2_layout.addWidget(self.url2_edit)
        layout.addLayout(url2_layout)

        href_layout = QHBoxLayout()
        href_label = QLabel('按钮 href:')
        self.href_edit = QLineEdit(self.config["href"])
        href_layout.addWidget(href_label)
        href_layout.addWidget(self.href_edit)
        layout.addLayout(href_layout)

        driver_path_layout = QHBoxLayout()
        driver_path_label = QLabel('ChromeDriver 路径:')
        self.driver_path_edit = QLineEdit(self.config["driver_path"])
        driver_path_layout.addWidget(driver_path_label)
        driver_path_layout.addWidget(self.driver_path_edit)
        layout.addLayout(driver_path_layout)

        user_data_dir_layout = QHBoxLayout()
        user_data_dir_label = QLabel('用户数据目录:')
        self.user_data_dir_edit = QLineEdit(self.config["user_data_dir"])
        user_data_dir_layout.addWidget(user_data_dir_label)
        user_data_dir_layout.addWidget(self.user_data_dir_edit)
        layout.addLayout(user_data_dir_layout)

        submit_button = QPushButton('提交')
        submit_button.clicked.connect(self.on_submit)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def on_submit(self):
        time = self.time_edit.time().toString("HH:mm")
        url1 = self.url1_edit.text()
        url2 = self.url2_edit.text()
        href_value = self.href_edit.text()
        driver_path = self.driver_path_edit.text()
        user_data_dir = self.user_data_dir_edit.text()

        save_config({
            "url1": url1,
            "url2": url2,
            "href": href_value,
            "driver_path": driver_path,
            "user_data_dir": user_data_dir,
            "time": time,
        })

        logging.info(f"已保存配置：{url1}, {url2}, {href_value}, {driver_path}, {user_data_dir}, {time}")

        schedule.clear()
        schedule.every().day.at(time).do(open_and_click_by_href, url1, href_value, driver_path, user_data_dir)
        schedule.every().day.at(time).do(open_and_click_by_href, url2, href_value, driver_path, user_data_dir)
        logging.info(f"任务已设置为每天 {time} 运行")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    setup_logging()  # 初始化日志
    app = QApplication(sys.argv)
    ex = SchedulerApp()
    ex.show()

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    sys.exit(app.exec_())
