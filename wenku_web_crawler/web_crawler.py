# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup  # 提取网页中需要的内容
import re
import time
# 走网页前端,故使用selenium库
from selenium import webdriver
from selenium.webdriver.common.by import By
import os, shutil  # 文件操作
from PIL import Image  # 图片操作
import threading  # 多线程优化


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


def sign_in(cookie_path, url):
    with open(cookie_path, 'r') as f:
        cookie_string = f.read()
        cookie_string = re.sub("true", "True", cookie_string)
        cookie_string = re.sub("false", "False", cookie_string)
        cookie_list = list(eval(cookie_string))
    for cookie in cookie_list:
        if cookie['sameSite']:
            cookie.pop('sameSite')
        driver.add_cookie(cookie)
    driver.get(url)  # 打开页面


def get_clean_window(num_of_pages, wenku_id, cookie_path):  # 登录百度文库，点击“展开”，并将不需要的页面元素（如广告）删除
    global isnt_sign_in
    url = "https://wenku.baidu.com/view/" + wenku_id + ".html"
    driver.get(url)

    try:
        if isnt_sign_in:  # 登录过就无需重复登录
            raise
    except:  # 实际的判断语句是这句
        sign_in(cookie_path, url)
        isnt_sign_in = False

    time.sleep(3)  # 这个3秒很重要
    try:  # 可能没有
        card = driver.find_element(By.CLASS_NAME, "experience-card-content")  # 弹出奇怪的东西
        close = card.find_element(By.CLASS_NAME, "close-btn")
        close.click()  # 关掉
        time.sleep(1)
    except:
        pass
    try:
        while True:
            read_all = driver.find_element(By.CLASS_NAME, "read-all")  # 展开
            driver.execute_script("arguments[0].click();", read_all)  # 聚焦并点击

    except:  # 可能不需要展开，也可能要展开多次(页数大于50)
        pass
    remove_list = ["//div[@class='header-wrapper no-full-screen new-header']",
                   "//div[@class='left-wrapper zoom-scale']/div[@class='no-full-screen']",
                   "//div[@class='reader-wrap']/div/div[@class='reader-topbar']",
                   "//div[@class='right-wrapper no-full-screen']",
                   "//div[@class='theme-enter-wrap']",
                   "//div[@class='lazy-load']/div[@class='sidebar-wrapper']",
                   "//div[@class='try-end-fold-page fold-static']",
                   "//div[@class='left-wrapper zoom-scale']/div[@class='no-full-screen']",
                   "//div[@class='lazy-load']",
                   "//div[@class='try-end-fold-page']"]  # 除广告及水印外所有需删除的元素
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


def get_screenshot(scr_list, num_of_pages, title, scr_path_):
    driver.execute_script("var q=document.documentElement.scrollTop=0")  # 回到顶部
    try:
        driver.maximize_window()  # 全屏显示
    except:
        pass
    # time.sleep(1)

    page_height = 680  # 实际为730,截多一点

    times = int(int(num_of_pages) * 2.4)
    # type(num_of_pages) = str, 已知一个23页的图片，可截出38张图，38/23 = 1.65，可是要*2.4才能保证拉到底端

    for i in range(times + 1):  # 加载图片
        js = "var q=document.documentElement.scrollTop=" + str(i * page_height)
        driver.execute_script(js)
        time.sleep(0.2)
        if i == times - 1:
            h1 = driver.find_element(By.TAG_NAME, "body").size["height"]
        if i == times:
            h2 = driver.find_element(By.TAG_NAME, "body").size["height"]
            if h2 != h1:  # 如果页面高度仍然在变化
                while not h2 == h1:  # 循环至不变为止
                    i += 1
                    js = "var q=document.documentElement.scrollTop=" + str(i * page_height)
                    driver.execute_script(js)
                    time.sleep(0.2)
                    h3 = driver.find_element(By.TAG_NAME, "body").size["height"]
                    h1, h2 = h2, h3

    height = driver.find_element(By.TAG_NAME, "body").size["height"]
    times = height // page_height

    driver.execute_script("var q=document.documentElement.scrollTop=0")  # 回到顶部
    if times <= 7:  # 如果文档比较小
        times += 2  # 可能出现截不到底的情况
    for i in range(times + 1):
        js = "var q=document.documentElement.scrollTop=" + str(i * page_height)
        driver.execute_script(js)

        make_path(scr_path_)

        scr_path = scr_path_ + title + "//"
        if not os.path.exists(scr_path):
            os.mkdir(scr_path)
        scr_name = scr_path + str(i + 1) + ".png"
        scr_list.append(scr_name)
        time.sleep(0.1)
        driver.save_screenshot(scr_name)

    img_I = Image.open(scr_list[-1])
    img_next_I = Image.open(scr_list[-2])
    while img_I == img_next_I:  # 先删除重复图片
        os.remove(scr_list[-1])  # 先删图
        del scr_list[-1]  # 再删路径
        img_I = Image.open(scr_list[-1])
        img_next_I = Image.open(scr_list[-2])


def judge(img, next_img, pics_in):  # 判断图片是否完整
    threshold = 210  # 定义灰度界限
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    img = img.convert('L')
    bw_img = img.point(table, '1')  # 图片二值化

    size = bw_img.size
    # print(("size is:{}").format(size))
    w = size[0]
    bw_img_list = bw_img.load()  # 获取像素点
    black = 0
    white = 0
    for i in range(w):
        data = bw_img_list[i, 0]
        # print(("data is:{}").format(data))
        if data == 0:
            black += 1
        else:
            white += 1
    # print(("black is:{}, white is:{}").format(black, white))
    if black == 0:
        return True  # 图片完整
    else:
        if img == next_img:  # 若与下一张图一样
            return True  # 那它还是完整的（排除表格影响）
        return False  # 图片不完整


def judge_2(IM, next_IM):  # 竖向检测
    if IM == next_IM:
        return False
    else:
        return True


def get_lines(im, num_of_lines, pics_in):
    im = im.rotate(180)  # 翻转
    l, w = im.size
    change_times = 0
    judgement = True
    first_i = 0  # 否则图片间会有没删掉的空白部分
    if pics_in:
        last_i = 50
    else:
        for i in range(w):
            if i < w:  # 牺牲时间，防止重复
                box = (0, i, l, i + 1)
                IM = im.crop(box)
                next_IM = im.crop((0, i, l, i + 1))
                JUDGEMENT = judge(IM, next_IM, pics_in)
                if JUDGEMENT == judgement:  # 相同则过
                    continue
                else:
                    judgement = JUDGEMENT  # 若不同，执行下头的代码
                change_times += 1  # 记变换一次
                # if change_times == 1:
                # first_i = i#若第一次变换，记录坐标
                if change_times % 2 == 0:  # 若为偶数次变换，则是截到了整行
                    line = 1  # 有一行字了
                    last_i = i
                    if change_times / 2 == num_of_lines:  # 变换次数除以2，即为截到的行数
                        last_i = i  # 记录下坐标
                        break
            elif line:
                pass
            else:  # 整页都是图片
                if w <= 50:
                    last_i = w
                else:
                    last_i = 50
    box = (0, first_i, l, last_i)
    im_lines = im.crop(box)  # 裁剪
    im_lines = im_lines.rotate(180)  # 翻转
    return im_lines


def duplicate_removal(path, next_path, pics_in):  # 去重
    im = Image.open(path)
    next_im = Image.open(next_path)
    num_of_lines = 2
    im_lines = get_lines(im=im, num_of_lines=num_of_lines, pics_in=pics_in)
    length_of_lines = im_lines.size[1]
    l, w = next_im.size
    for i in range(w):
        box = (0, i, l, i + length_of_lines)
        next_im_lines = next_im.crop(box)
        if im_lines == next_im_lines:
            new_box = (0, i + length_of_lines, l, w)
            next_im = next_im.crop(new_box)
            next_im.save(next_path)
            break
    try:
        type(del_path)
    except NameError:  # 若未定义
        del_path = False
    return del_path


def crop_pictures(scr_list, pics_in):
    for path in scr_list:
        # print(("现在是{}").format(path))
        im = Image.open(path)
        # print(("im.size is:{}").format(im.size))
        l, w = im.size
        box = (0, 0, l - 25, w)
        im = im.crop(box)  # 削去下拉条
        '''不需要再判断图片是否完整了
        l,w = im.size
        for i in range(w):#自上而下遍历图片的每一行
            box = (0,i,l,i+1)#左上右下
            IM = im.crop(box)
            next_IM = im.crop((0,i+1,l,w))
            judgement = judge(IM,next_IM,pics_in)
            if judgement:
                if i != 0:
                    new_box = (0,i,l,w)
                    im = im.crop(new_box)
                    #print(("this part worked"))
                break
            else:
                continue
        im = im.rotate(180)#翻转
        l,w = im.size#图片大小可能出现变化
        for i in range(w):#自上而下遍历图片的每一行
            box = (0,i,l,i+1)#左上右下
            IM = im.crop(box)
            next_IM = im.crop((0,i+1,l,w))
            judgement = judge(IM,next_IM,pics_in)
            if judgement:
                if i != 0:
                    new_box = (0,i,l,w)
                    im = im.crop(new_box)
                    #print(("this part worked"))
                break
            else:
                continue
        #不转了
        '''
        im = im.rotate(180)  # 弥补原先程序（已删）中的翻转
        # 接下来进行竖直分割
        l, w = im.size
        l_list = []
        ll = 0
        while ll < l:
            l_list.append(ll)
            ll += 4  # 四行截一次
        for i in l_list:  # 从左往右
            box = (i, 0, i + 1, w)
            IM = im.crop(box)
            next_box = (i + 4, 0, i + 5, w)
            next_IM = im.crop(next_box)
            if judge_2(IM=IM, next_IM=next_IM):
                # 类似二分法进行细化检测
                for j in range(i, i + 4 + 1):  # 前闭后开故末尾+1
                    box = (j, 0, j + 1, w)
                    IM = im.crop(box)
                    next_box = (j + 1, 0, j + 2, w)
                    next_IM = im.crop(next_box)
                    if judge_2(IM, next_IM):
                        new_box = (j + 1, 0, l, w)
                        im = im.crop(new_box)
                        break
                break
            else:
                continue
        im = im.rotate(180)  # 这时候再转
        l, w = im.size
        l_list = []
        ll = 0
        while ll < l:
            l_list.append(ll)
            ll += 2  # 两行截一次
        for i in l_list:  # 从左往右
            box = (i, 0, i + 1, w)
            IM = im.crop(box)
            next_box = (i + 4, 0, i + 5, w)
            next_IM = im.crop(next_box)
            if judge_2(IM=IM, next_IM=next_IM):
                for j in range(i, i + 4 + 1):
                    box = (j, 0, j + 1, w)
                    IM = im.crop(box)
                    next_box = (j + 1, 0, j + 2, w)
                    next_IM = im.crop(next_box)
                    if judge_2(IM, next_IM):
                        new_box = (j + 1, 0, l, w)
                        im = im.crop(new_box)
                        break
                break
            else:
                continue
        im.save(path)
    for i in range(len(scr_list)):  # 去重
        if not i == len(scr_list) - 1:  # 不是最后一个的话
            path = scr_list[i]
            next_path = scr_list[i + 1]
            del_path = duplicate_removal(path=path, next_path=next_path, pics_in=pics_in)
            if del_path:  # 若出现
                break  # 退出循环
    if del_path:
        del_i = scr_list.index(del_path)
        if del_i == len(scr_list) - 1:  # 那么这是最后一张图了
            os.remove(scr_list[-1])  # 先删图
            del scr_list[-1]  # 再删路径
        else:
            times = len(scr_list) - del_i
            for i in range(times):
                os.remove(scr_list[-1])
                del scr_list[-1]


def paste_images(im_path):
    lw_list = []  # 记录图片长宽
    im_list = []  # 记录图片路径
    for i in os.listdir(im_path):
        im_list.append(int(i.split(".")[0]))  # 字符串与数字排列方式不同：1,2,10;'1','10','2'
    im_list.sort()
    img_list = []
    for i in im_list:
        img_list.append(im_path + "\\" + str(i) + ".png")
    for path in img_list:
        im = Image.open(path)
        lw_list.append(im.size)

    l0 = lw_list[0][0]
    w0 = 0
    for l, w in lw_list:
        if l > l0:
            l0 = l
        w0 += w
    size = (l0, w0)

    img_0 = Image.new("RGB", size)  # 新建底图
    li, wi = 0, 0
    i = 0
    for i in range(len(img_list)):
        img_i = Image.open(img_list[i])
        l, w = lw_list[i]
        box = (li, wi, li + l, wi + w)
        img_0.paste(img_i, box)
        wi = wi + w
        i += 1

    img_0.save(im_path + ".png")


def web_crawler(wenku_id, pics_in, scr_path_, cookie_path):
    title, num_of_pages = get_info(wenku_id=wenku_id)  # 首先拿到标题和总页数
    get_clean_window(wenku_id=wenku_id, num_of_pages=num_of_pages, cookie_path=cookie_path)  # 把窗口的各种影响阅读的弹窗清一遍
    time.sleep(1)
    scr_list = []
    get_screenshot(scr_list, num_of_pages, title, scr_path_)  # 屏幕截图
    return scr_list, pics_in, title


def img_process(scr_list, pics_in, title, scr_path_):  # 后台进程
    crop_pictures(scr_list, pics_in)  # 将不必要的部分裁去
    paste_images(im_path=scr_path_ + title)  # 传入文件夹名称
    shutil.rmtree(scr_path_ + title)  # 删除文件夹


def main(id_list, scr_path_, cookie_path):
    global driver  # 驱动仅有一个，故直接全局化
    global isnt_sign_in  # 未登录
    isnt_sign_in = True
    driver = webdriver.Chrome()  # 用谷歌,只能用谷歌,用火狐的话要改好多

    if len(id_list) == 1:
        scr_list, pics_in, title = web_crawler(id_list[0], True, scr_path_, cookie_path)
        driver.quit()
        img_process(scr_list, pics_in, title, scr_path_)
    else:
        for i in range(len(id_list)):
            try:
                t_start = time.time()
                scr_list, pics_in, title = web_crawler(id_list[i], True, scr_path_, cookie_path)
                t_end = time.time()
                run_time = t_end - t_start
                if i == len(id_list) - 1:
                    driver.quit()
                elif run_time > 200:  # 运行时间超过200秒
                    driver.quit()
                    driver = webdriver.Chrome()  # 重开浏览器
                    isnt_sign_in = True  # 登录信息随之失效
                # img_process(scr_list,pics_in,title,scr_path_)#无多线程优化
                threading.Thread(target=img_process, args=(scr_list, pics_in, title, scr_path_)).start()  # 多线程优化
                continue
            except:
                title, num_of_pages = get_info(id_list[i])
                print("id为“{}”的文档出错，其标题为：“{}”".format(id_list[i], title))
                if i == len(id_list) - 1:
                    driver.quit()
                continue
