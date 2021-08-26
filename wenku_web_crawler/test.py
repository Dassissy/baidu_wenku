import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from functools import wraps


def logit(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        ti2 = time.asctime(time.localtime(time.time()))
        log_string_0 = ti2 + " : " + func.__name__ + "  began"
        func(*args, **kwargs)
        ti2 = time.asctime(time.localtime(time.time()))
        log_string_1 = ti2 + " : " + func.__name__ + "  finished"
        with open("D://wenku_pics//logfile.log", "w") as f:
            f.write(log_string_0 + "\n")
            f.write(log_string_1 + "\n")

    return with_logging


@logit
def add(x):
    print(5*x)
    time.sleep(1)
    return 5 * x


if __name__ == "__main__":
    add(5)
