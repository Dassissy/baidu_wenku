import time

from selenium import webdriver

d = webdriver.Chrome()
time.sleep(1)
d.quit()
d = webdriver.Chrome()
time.sleep(1)