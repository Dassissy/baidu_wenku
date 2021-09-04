# -*- coding: utf-8 -*-
from tkinter import *
import requests
from bs4 import BeautifulSoup  # 提取网页中需要的内容
import re
import time
# 走网页前端,故使用selenium库
from selenium import webdriver
from selenium.webdriver.common.by import By
import os  # 文件操作
from PIL import Image  # 图片操作
import threading  # 多线程优化
from selenium.webdriver.chrome.options import Options
import queue
from functools import update_wrapper, wraps


def get_info(wenku_id):  # 拿到一些信息
    url = "https://wenku.baidu.com/view/" + wenku_id + ".html"
    try:
        r = requests.get(url)
    except:
        return "ERROR"
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find('title').string
    title = title.split(' ')[0]
    dividers = soup.find_all("span", attrs={'class': 'divider'})
    divider = dividers[-1]
    num_of_pages = divider.find_next().string[:-1]
    return title, num_of_pages


def sign_in(cookie_path, url, driver):
    with open(cookie_path, 'r') as f:
        cookie_string = f.read()
        cookie_string = re.sub("true", "True", cookie_string)
        cookie_string = re.sub("false", "False", cookie_string)
        cookie_list = list(eval(cookie_string))
    for cookie in cookie_list:
        if cookie['sameSite']:
            cookie.pop('sameSite')
        driver.add_cookie(cookie)
    driver.get(url)  # 重新打开页面


def get_clean_window(wenku_id, cookie_path, driver, work_queue, title):
    # 登录百度文库，点击“展开”，并将不需要的页面元素（如广告）删除

    work_queue[title] = "链接到文库"

    url = "https://wenku.baidu.com/view/" + wenku_id + ".html"
    driver.get(url)

    work_queue[title] = "登录"

    sign_in(cookie_path, url, driver)
    time.sleep(3)  # 这个3秒很重要

    work_queue[title] = '删除弹窗'

    try:  # 可能没有
        card = driver.find_element(By.CLASS_NAME, "experience-card-content")  # 弹出奇怪的东西
        close = card.find_element(By.CLASS_NAME, "close-btn")
        close.click()  # 关掉
        time.sleep(1)
    except:
        pass
    try:

        work_queue[title] = "展开"

        while True:
            read_all = driver.find_element(By.CLASS_NAME, "read-all")  # 展开
            driver.execute_script("arguments[0].click();", read_all)  # 聚焦并点击

    except:  # 可能不需要展开，也可能要展开多次(页数大于50)
        pass

    work_queue[title] = "删除广告"

    with open("remove_list.txt") as f:
        remove_list = eval(f.read())  # 除广告及水印外所有需删除的元素

    for ele_path in remove_list:
        try:
            ele = driver.find_element(By.XPATH, ele_path)
            driver.execute_script("""var element = arguments[0];
                                  element.parentNode.removeChild(element)""", ele)  # 第一句是在传入ele，第二句执行删除
        except:
            continue
    hx_warp_x_path = "//div[@class='hx-warp']"  # 接下来对广告下手
    hx_warps = driver.find_elements(By.XPATH, hx_warp_x_path)
    for hx in hx_warps:
        driver.execute_script("""var element = arguments[0];
                              element.parentNode.removeChild(element)""", hx)


# 问题：水印可以被定位，但无法被删除，原因：加密

def make_path(scr_path_):
    scr_path_list = scr_path_.split("//")[:-1]
    PATH = scr_path_list[0]
    for i in range(1, len(scr_path_list)):
        PATH = PATH + r"//" + scr_path_list[i]
        if not os.path.exists(PATH):
            os.mkdir(PATH)


def get_screenshot(num_of_pages, title, scr_path_, driver, work_queue):
    driver.execute_script("var q=document.documentElement.scrollTop=0")  # 回到顶部

    screen_height = 680  # 实际为730,截多一点
    page_height = driver.find_element(By.ID, "pageNo-1").size["height"]
    page_height_all = page_height * int(num_of_pages)
    times = int(page_height_all / screen_height)  # FIXME 可能出错
    # type(num_of_pages) = str, 注意：文字文档和图档的页高并不相同

    work_queue[title] = "遍历文档"

    for i in range(times + 1):  # 加载图片
        js = "var q=document.documentElement.scrollTop=" + str(i * screen_height)
        driver.execute_script(js)

        work_queue[title] = "遍历文档：{} / {}".format(i, times)

        time.sleep(0.2)
        if i == times - 1:
            h1 = driver.find_element(By.TAG_NAME, "body").size["height"]
        if i == times:
            h2 = driver.find_element(By.TAG_NAME, "body").size["height"]
            if h2 != h1:  # 如果页面高度仍然在变化
                while not h2 == h1:  # 循环至不变为止
                    i += 1
                    js = "var q=document.documentElement.scrollTop=" + str(i * screen_height)
                    driver.execute_script(js)

                    work_queue[title] = "遍历文档：{} / {}".format(i, times)

                    time.sleep(0.2)
                    h3 = driver.find_element(By.TAG_NAME, "body").size["height"]
                    h1, h2 = h2, h3

    time.sleep(3)  # 此时页面中可能出现一些会自动消失的小贴士

    if (i+2) * screen_height > 45000:  # 如果页面非常非常大
        # 那就不可以直接截图，要分成好几块
        page_num = (i+2) * screen_height // 25000 + 1  # 不知为何，总是会少掉2页
        page_h = round((i+2) * screen_height / page_num, 2)

        work_queue[title] = "设置窗体大小"

        driver.set_window_size(width=1500, height=page_h)
        for num in range(page_num):
            
            work_queue[title] = "截图中：{} / {}".format(num+1, page_num)

            js = "var q=document.documentElement.scrollTop=" + str(num * page_h)
            driver.execute_script(js)
            make_path(scr_path_ + title + "//")
            scr_name = scr_path_ + title + "//" + str(num+1) + ".png"
            driver.get_screenshot_as_file(scr_name)  # 保存
            process_thread = threading.Thread(target=just_body, args=(scr_name, {}, title))  # 另起一个线程进行图片处理
            process_thread.start()
            # process_thread.join()
        
        work_queue[title] = "结束"
        del work_queue[title]
    
    else:

        work_queue[title] = "设置窗体大小"

        driver.set_window_size(width=1500, height=(i+1+1)*screen_height)  # 比body元素大一圈，这样没有下拉条

        work_queue[title] = "截图"

        make_path(scr_path_)
        scr_name = scr_path_ + title + ".png"
        driver.get_screenshot_as_file(scr_name)  # 保存

        work_queue[title] = "去边框"

        just_body(scr_name, work_queue, title)  # 去边框

        work_queue[title] = "结束"
        del work_queue[title]


def just_body(scr_name, work_queue, title):
    """
    只需要图片的内容部分，所以要对边框进行处理
    百度文库的正文内容背景色是纯白，边框一般是灰色(244,244,244)，但有时会换成其它图案
    因此，这里是通过把不是纯白的部分看成是边框并删除，以此达到去边框的效果
    同时必须先进行横向的去边框，因为横向的边框可能会对纵向的有较大影响
    """

    scrshot = Image.open(scr_name)  # 打开图片
    # 先从 横向 上方 开始
    work_queue[title] = "去边框 横向 上方"

    l, w = scrshot.size
    w_list = [i for i in range(w)][::4]  # 检测思路类似二分法，不过这里是每隔4像素检测一次
    for i in w_list:
        box = (0, i, l, i+1)
        im = scrshot.crop(box)
        pl0 = im.load()  # 获取像素点
        point_list: list = [pl0[i, 0] for i in range(l)]
        # 横向时，如果像素点列表中的白色数量大于列表长度的 1/2 ，则认为它是“正文 ”
        if point_list.count((255, 255, 255, 255)) >= len(point_list) / 2:
            while True:  # 这时再向前寻找”边界“
                i -= 1
                box = (0, i, l, i + 1)
                im = scrshot.crop(box)
                pl0 = im.load()  # 获取像素点
                point_list: list = [pl0[i, 0] for i in range(l)]
                if not point_list.count((255, 255, 255, 255)) >= len(point_list) / 2:  # 找到边界处的i值
                    i += 1  # 这样截出来才是正文
                    break  # 结束循环
            box = (0, i, l, w)
            scrshot = scrshot.crop(box)
            break

    #  翻转图片
    scrshot = scrshot.rotate(180)
    # 横向 下方
    work_queue[title] = "去边框 横向 下方"

    l, w = scrshot.size
    w_list = [i for i in range(w)][::4]  # 检测思路类似二分法，不过这里是每隔4像素检测一次
    for i in w_list:
        box = (0, i, l, i + 1)
        im = scrshot.crop(box)
        pl0 = im.load()  # 获取像素点
        point_list: list = [pl0[i, 0] for i in range(l)]
        if point_list.count((255, 255, 255, 255)) >= len(point_list) / 2:
            while True:  # 这时再向前寻找”边界“
                i -= 1
                box = (0, i, l, i + 1)
                im = scrshot.crop(box)
                pl0 = im.load()  # 获取像素点
                point_list: list = [pl0[i, 0] for i in range(l)]
                if not point_list.count((255, 255, 255, 255)) >= len(point_list) / 2:  # 找到边界处的i值
                    i += 1  # 这样截出来才是正文
                    break  # 结束循环
            box = (0, i, l, w)
            scrshot = scrshot.crop(box)
            break

    # 纵向 右侧，此时超过 2/3 才算判定成功
    work_queue[title] = "去边框 纵向 右侧"

    l, w = scrshot.size
    l_list = [i for i in range(l)][::4]
    for i in l_list:
        box = (i, 0, i + 1, w)
        im = scrshot.crop(box)
        pl0 = im.load()  # 获取像素点
        point_list: list = [pl0[0, i] for i in range(w)]
        if point_list.count((255, 255, 255, 255)) >= len(point_list) * 2 / 3:
            while True:  # 这时再向前寻找”边界“
                i -= 1
                box = (i, 0, i + 1, w)
                im = scrshot.crop(box)
                pl0 = im.load()  # 获取像素点
                point_list: list = [pl0[0, i] for i in range(w)]
                if not point_list.count((255, 255, 255, 255)) >= len(point_list) * 2 / 3:  # 找到边界处的i值
                    i += 1  # 这样截出来才是正文
                    break  # 结束循环
            box = (i, 0, l, w)
            scrshot = scrshot.crop(box)
            break

    scrshot = scrshot.rotate(180)
    # 接着是 纵向 左侧，此时超过 2/3 才算判定成功
    work_queue[title] = "去边框 纵向 左侧"

    l, w = scrshot.size
    l_list = [i for i in range(l)][::4]
    for i in l_list:
        box = (i, 0, i+1, w)
        im = scrshot.crop(box)
        pl0 = im.load()  # 获取像素点
        point_list: list = [pl0[0, i] for i in range(w)]
        if point_list.count((255, 255, 255, 255)) >= len(point_list) * 2 / 3:
            while True:  # 这时再向前寻找”边界“
                i -= 1
                box = (i, 0, i+1, w)
                im = scrshot.crop(box)
                pl0 = im.load()  # 获取像素点
                point_list: list = [pl0[0, i] for i in range(w)]
                if not point_list.count((255, 255, 255, 255)) >= len(point_list) * 2 / 3:  # 找到边界处的i值
                    i += 1  # 这样截出来才是正文
                    break  # 结束循环
            box = (i, 0, l, w)
            scrshot = scrshot.crop(box)
            break

    work_queue[title] = "保存"

    scrshot.save(scr_name)  # 直接保存


def title_list_duplicate_removal(ID_list, scr_path):
    # 针对标题的去重
    have_had_id_list = os.listdir(scr_path)
    have_had_id_list = [have_had_id_list[i].lower() for i in range(len(have_had_id_list))]  # 小写化
    title_list: list = []
    for i in range(len(ID_list)):
        title_list.append(ID_list[i][1].lower() + ".png")  # 小写化
    for i in range(len(title_list)):
        title = title_list[i]
        if title in have_had_id_list or title_list.count(title) > 1:  # 如果已存在
            time_now = str(time.time()).split(".")
            time_now = time_now[0] + time_now[1]
            title = ID_list[i][1] + "_" + time_now  # 修改title（加上时间后缀）（此时不加.png，也无需小写）
            ID_list[i][1] = title
            time.sleep(0.1)  # 如果此时不暂停，那么可能在添加后缀之后文件名仍然相同（未判明）


def web_crawler(wenku_id, title, num_of_pages, scr_path_, cookie_path, work_queue):

    try:

        work_queue[title] = "开始"

        op = Options()
        op.add_argument('--headless')
        op.add_argument('--disable-gpu')
        op.add_argument('--log-level=4')
        driver = webdriver.Chrome(options=op)  # 用谷歌的无头浏览器
        get_clean_window(wenku_id=wenku_id, cookie_path=cookie_path,
                        driver=driver, work_queue=work_queue, title=title)  # 把窗口的各种影响阅读的弹窗清一遍
        time.sleep(1)
        get_screenshot(num_of_pages, title, scr_path_, driver, work_queue)  # 屏幕截图并保存（长图）

    except:  # 捕捉错误

        work_queue[title] = "在{}时出错了！".format(work_queue[title])


def logit(func):  # 打日志，还没想好怎么用
    @wraps(func)
    def with_logging(*args, **kwargs):
        ti2 = time.asctime(time.localtime(time.time()))
        log_string_0 = ti2 + " : " + func.__name__ + "  began"
        func(*args, **kwargs)
        ti2 = time.asctime(time.localtime(time.time()))
        log_string_1 = ti2 + " : " + func.__name__ + "  finished"
        with open("D://wenku_pics//logfile.log", "a") as f:
            f.write(log_string_0 + "\n")
            f.write(log_string_1 + "\n")

    return with_logging



class Crawler:
    def __init__(self, id_list, scr_path_, cookie_path):
        self.id_list = id_list
        self.scr_path_ = scr_path_
        self.cookie_path = cookie_path
        self.work_queue: dict = {}  # FIXME 打日志
        self.progress_bar_thread = threading.Thread(target=self.update_varstring)
        self.progress_bar_thread.setName("progress_bar_thread")
        self.lock = threading.Lock()


    @property
    def finished(self):
        if self.progress_bar_thread.is_alive():
            return False
        else:
            return True


    def update_varstring(self):
        global progress_bar_txt, tl
        self.work_queue[self.id_list[0][1]] = "初始化中..."  # 征用一下work_queue的第一个位置
        ERROR = False
        time0 = time.time()
        while True:
            # 获取进度文本
            progress_bar_list = eval(str([str(key) + ":" + str(self.work_queue[key]) + "\n" for key in self.work_queue]))
            var_txt = ''
            for txt in progress_bar_list:
                var_txt += txt
            time1 = time.time()
            time_txt = "计时：" + str(round(time1-time0, 2))
            progress_bar_txt.set(var_txt + "\n "+ time_txt)
            if var_txt == '':
                break
            elif len(self.work_queue.values()) == len(re.findall(r"在.*?时出错了！", str(self.work_queue.values()))):  # 如果所有内容都是出错信息的话
                ERROR = True
                break
            # 隔一段时间打一次进度
            time.sleep(0.1)
            tl.update()
        if not ERROR:  # 如果没有发生错误
            tl.destroy()  # 删除窗体


    def crawler_begin(self):
        id_list = self.id_list
        scr_path_ = self.scr_path_
        cookie_path = self.cookie_path

        i = 0
        while i < len(id_list):
            if len(self.work_queue) < 10:  # 最大并发数为10
                crawler_thread = threading.Thread(target=web_crawler,
                                                    args=(id_list[i][0], id_list[i][1], id_list[i][2],
                                                        scr_path_, cookie_path, self.work_queue))
                self.work_queue[id_list[i][1]] = "线程已创建"
                crawler_thread.start()
                i += 1
            else:
                time.sleep(0.5)


    @logit
    def begin(self):
        global progress_bar_txt, tl, progress_bar_thread
        tl = Toplevel()
        tl.title("进度框")
        # 通过进度框显示内容
        progress_bar_txt = StringVar()
        progress_bar_txt.set("稍等片刻，爬虫已经启动，所有预设线程都在忙碌...")
        progress_bar_label = Label(tl, textvariable=progress_bar_txt, anchor="w", justify="left")
        progress_bar_label.grid()
        tl.update()
        self.progress_bar_thread.start()
        self.crawler_begin() # 启动爬虫
