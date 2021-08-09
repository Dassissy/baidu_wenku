from tkinter import Tk, Label, Entry, Button, Frame, Toplevel
from web_crawler import main as web_crawler, make_path
from web_crawler import get_info
import time


def ety(x, y):  # 创建新的输入框
    e = Entry(main_entry_frame)
    e.grid(column=x, row=y)
    return e


def save(e, y):  # 保存程序
    txt = e.get()
    # print("e.winfo_geometry() is:{}".format(e.winfo_geometry()))
    id_list[y - 1] = txt  # 可修改
    try:
        title, num_of_pages = get_info(txt)  # 若id出错，这一步会报错
        l = Label(main_entry_frame, text="已保存:" + title + " : " + num_of_pages + "页")
        l.grid(column=2, row=y)

        if len(es_dict[e]) == 2:
            es_dict[e].append(title)
            es_dict[e].append(num_of_pages)
        else:
            es_dict[e][2] = title
            es_dict[e][3] = num_of_pages

        try:
            if error_l:  # 如果有出错信息存在
                error_l.grid_forget()  # 那就删了
        except:
            pass

    except:
        if txt == '':  # 如果出错原因是无id
            id_list[y - 1] = ''
            l = Label(main_entry_frame, text="未检测到id！！")
            l.grid(column=2, row=y)
        else:  # 如果出错原因不是无id
            id_list[y - 1] = ''
            l = Label(main_entry_frame, text="id出错了！！")
            l.grid(column=2, row=y)


def save_btn(e, x, y):  # 保存按钮
    save_btn = Button(main_entry_frame, text="这是第" + str(y) + "个id：点击以保存", command=lambda: save(e, y))
    save_btn.grid(column=x, row=y)
    return save_btn


def continue_this_part(x, y, y_btn, finish_btn):  # 继续输入按钮
    id_list.append('')  # 在id_list中为每个输入框留下位置
    y_btn.destroy()
    finish_btn.destroy()
    try:
        f_l.grid_forget()
    except:
        pass
    entry_entry(x, y)  # 递归


def begin(x, y):  # 开始爬取
    global error_l, time_label  # 出错信息全局共享，时间信息方便删
    f_l.grid_forget()
    # print("id_list is:{}".format(id_list))
    
    # 先进行保存
    for e in es_dict:
        if len(es_dict[e]) == 2:  # 如果该输入框没有启动过保存程序
            y = es_dict[e][1]
            save(e, y)  # 那就启动

    ID_list = []  # ID_list是准备传输给爬虫程序的，删除了出错id的列表
    for ID in id_list:
        if not ID == '':
            ID_list.append(ID)
    if ID_list:
        try:
            time_label.grid_forget()
        except:
            pass

        time_start = time.time()  # 记录耗时
        scr_path_ = scr_path + scr_name + r"//"
        web_crawler(ID_list, scr_path_, cookie_path)  # 启动爬虫
        time_end = time.time()
        TIME = time_end - time_start

        f_l.grid(column=x, row=y + 3)
        time_label = Label(main_entry_frame, text="耗时： " + str(TIME) + " 秒")
        time_label.grid(column=x + 1, row=y + 3)

    else:  # 如果此列表全空，那么就是所有的id都出错了
        error_l = Label(main_entry_frame, text="所有的id都出错了，请在更改后重试！！")
        error_l.grid(column=x, row=y + 3)


def yes_btn(x, y):
    global f_l
    f_l = Label(main_entry_frame, text="""爬虫已启动过，若不需要导出id，请关闭这个窗体
                还需要爬取的话，请再次点击“合成爬取方案”""")
    finish_btn = Button(main_entry_frame, text="开始爬取，记得要保存哦！", command=lambda: begin(x, y))
    finish_btn.grid(column=x, row=y)
    y_btn = Button(main_entry_frame, text="继续输入id点这里！", command=lambda: continue_this_part(x, y, y_btn, finish_btn))
    y_btn.grid(column=x + 1, row=y)


def entry_entry(x, y):
    e = ety(x, y)
    s_btn = save_btn(e, x + 1, y)

    es_dict[e] = [s_btn, y]

    yes_btn(x, y + 1)  # 由于使用了递归结构，此处传入y+1可看作是y+=1


def export_id(id_name_e):
    if id_name_e.get():
        id_name = id_name_e.get()
    else:
        id_name = "id_list"

    Path = scr_path + scr_name + "//" + id_name + ".txt"

    ID_list = []  # 先删除出错id
    for ID in id_list:
        if not ID == '':
            ID_list.append(ID)

    if ID_list:
        with open(Path, "w") as f:
            for ID in ID_list:
                f.write(ID + "\n")
            f.close()
    
        export_l = Label(main_entry_frame, text="已导出")
        export_l.grid(column=3, row=4)
    else:
        export_l = Label(main_entry_frame, text="无id！！")
        export_l.grid(column=3, row=4)

def make_main_entry():
    global es_dict, id_list  # 全局化
    global main_entry_frame
    es_dict = {}  # 输入框和输入信息的字典
    id_list = ['']  # 第一个空的初始化

    global cookie_path, scr_path, scr_name  # 配置全局化
    with open(r"config\config.txt", "r+") as f:  # 读写配置
        config_dict = eval(f.read())
    cookie_path = config_dict["cookie_path"]
    scr_path = config_dict["scr_path"]
    scr_name = config_dict["scr_name"]

    main_entry_frame = Frame(Toplevel())
    Label(main_entry_frame, text="在下方的框内输入id").grid(column=0, row=0)
    get_id_help_btn = Button(main_entry_frame, text="从链接中截取id的方法看这里！", command=get_id_help_labels)
    get_id_help_btn.grid(column=1, row=0)
    entry_entry(0, 1)

    id_name_e = Entry(main_entry_frame)
    id_name_e.grid(column=3, row=1)
    id_name_e.insert(0, "id_list")
    Label(main_entry_frame, text="""在下方输入导出id时的文件名
    （路径同图片存储路径）""").grid(column=3, row=0)
    export_id_btn = Button(main_entry_frame, text="点此导出id", command=lambda: export_id(id_name_e))
    export_id_btn.grid(column=3, row=2)

    main_entry_frame.grid()



def config_setting():
    global cookie_path_e, scr_path_e, scr_name_e, config_save_btn, cookie_path, scr_path, scr_name  # 配置全局化

    with open(r"config\config.txt", "r+") as f:  # 读写配置
        config_dict = eval(f.read())
    cookie_path = config_dict["cookie_path"]
    scr_path = config_dict["scr_path"]
    scr_name = config_dict["scr_name"]
    
    config_help_labels()
    
    cookie_frame = Frame(config_frame)
    cookie_path_e = Entry(master=cookie_frame, width=35)
    cookie_path_e.grid(column=1, row=0)
    cookie_path_e.insert(0, cookie_path)
    Label(cookie_frame, text="输入cookie的路径：").grid(column=0, row=0)
    cookie_frame.grid(column=0, row=3)
    
    scr_path_frame = Frame(config_frame)
    scr_path_e = Entry(master=scr_path_frame, width=35)
    scr_path_e.grid(column=1, row=0)
    scr_path_e.insert(0, scr_path)
    Label(scr_path_frame, text="输入总文件夹的路径：").grid(column=0, row=0)
    scr_path_frame.grid(column=0, row=5)
    
    scr_name_frame = Frame(config_frame)
    scr_name_e = Entry(master=scr_name_frame)
    scr_name_e.grid(column=1, row=0)
    scr_name_e.insert(0, scr_name)
    Label(scr_name_frame, text="输入本次爬取的储存路径：").grid(column=0, row=0)
    scr_name_frame.grid(column=0, row=7)

    config_save_btn = Button(config_frame, text="点此以保存配置", command=save_config)
    config_save_btn.grid(column=0, row=8)


def save_config():
    cookie_dict = {"cookie_path": cookie_path_e.get(), "scr_path": scr_path_e.get(), "scr_name": scr_name_e.get()}
    with open(r"config\config.txt", "w") as f:
        f.write(str(cookie_dict))
        f.close()

    scr_path_ = scr_path_e.get() + scr_name_e.get() + r"//"
    make_path(scr_path_)  # 先建立路径

    sl = Label(config_frame, text="已保存！")
    sl.grid(column=0, row=9)


def c_ety(x, y):  # 创建新的输入框
    e = Entry(master=config_frame)
    e.grid(column=x, row=y)
    return e


def make_config_frame():
    global config_frame
    config_frame = Frame(Toplevel())
    config_setting()
    config_frame.grid()
    

def tk_help_labels(window):  # 主页面上的说明文字
    # 这样文字会居中显示
    Label(window, text="你可以使用此程序方便地从百度文库上收集资料").grid(column=0, row=0)
    Label(window, text="在开始之前请先配置好selenium-webdriver").grid(column=0, row=1)
    Label(window, text="并且点击“设置配置”设置好配置").grid(column=0, row=2)
    Label(window, text="准备就绪后，点击下方按钮以开始运行").grid(column=0, row=3)
    Label(window, text="""请点击下方按钮以进行配置""").grid(column=0, row=5)
    Label(window, text="""请注意：不要同时开启两个或更多相同的窗体，会冲突的！！""").grid(column=0, row=7)


def config_help_labels():  # 配置页上的说明文字
    Label(config_frame, text="请注意：按照框内原有格式进行调整，如果调整后出错，").grid(column=0, row=0)
    Label(config_frame, text="可以把config//original_config.txt留下拷贝后重命名为config.txt以恢复出厂设置").grid(column=0, row=1)
    Label(config_frame, text="从已登录的百度文库中导出cookie后，以txt文档的形式存储，将其地址放入框内并保存").grid(column=0, row=2)
    Label(config_frame, text="“总文件夹”意为所有爬取下的图片的储存位置").grid(column=0, row=4)
    Label(config_frame, text="每次爬取可以爬取多个文档，它们可以保存在不同的文件夹中，它们都是“总文件夹”的子文件夹").grid(column=0, row=6)
    
    
def get_id_help_labels():  # 《如何截取id》
    get_id_frame = Frame(Toplevel())
    Label(get_id_frame, text="文库id的截取方式如下：").grid(column=0, row=0)
    Label(get_id_frame, text="这是一个文库链接 https://wenku.baidu.com/view/abc123def456ghi789.html").grid(column=0, row=1)
    Label(get_id_frame, text="而所谓“id”，就是中间“abc123def456ghi789”这一段").grid(column=0, row=2)
    Label(get_id_frame, text="在浏览器中截取id，只需要在这段字符中的任意位置双击鼠标即可").grid(column=0, row=3)
    Label(get_id_frame, text="截取后即可粘贴进id输入框中").grid(column=0, row=4)
    get_id_frame.grid()


def main():
    window = Tk()
    window.title("爬虫图形界面")
    tk_help_labels(window)
    main_entry_btn = Button(window, text="合成爬取方案", command=make_main_entry)
    main_entry_btn.grid(column=0, row=4)
    config_frame_btn = Button(window, text="设置配置", command=make_config_frame)
    config_frame_btn.grid(column=0, row=6)
    window.mainloop()


if __name__ == "__main__":
    main()
