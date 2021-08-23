import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

op = Options()
op.add_argument('--headless')
op.add_argument('--disable-gpu')
d = webdriver.Chrome(options=op)

d.get('https://www.baidu.com')
time.sleep(1)
d.save_screenshot("D://baidu_scrshot.png")
d.quit()
