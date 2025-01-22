# cflChromePick
PT自动签到

总体：浏览器打开指定网页，点击任意指定（href判定）按钮

![](/dist/ChromePick1.gif)


功能：
保持登录状态
模拟点击签到（点击按钮自行设置：根据href名称）
log日志
首次配置文件，后续不用再填写



python

安装

pip install selenium

pip install PyQt5


安装
pip install pyinstaller

pyinstaller --onefile --windowed cflChromePick.py


查看chrome浏览器版本
chrome://settings/help

下载对应ChromeDriver.exe
https://googlechromelabs.github.io/chrome-for-testing/


默认配置： 自行更改
[SETTINGS]
url1 = https://carpt.net/index.php
url2 = https://1ptba.com/index.php
href = attendance.php
driver_path = E:\A\program\vscode\python\ChromePick\chromedriver.exe
user_data_dir = E:\A\program\vscode\python\ChromePick\UserData
time = 19:21

