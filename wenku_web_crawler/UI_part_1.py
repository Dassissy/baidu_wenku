from tkinter import Tk, Label, Entry, Button, Frame

from web_crawler import make_path


def config_setting():
    global cookie_path_e, scr_path_e, scr_name_e, config_save_btn, cookie_path, scr_path, scr_name  # 配置全局化
    with open(r"config\config.txt", "r+") as f:  # 读写配置
        config_dict = eval(f.read())
    cookie_path = config_dict["cookie_path"]
    scr_path = config_dict["scr_path"]
    scr_name = config_dict["scr_name"]

    cookie_path_e = c_ety(1, 0)
    cookie_path_e.insert(0, cookie_path)
    Label(config_frame, text="输入cookie的路径：").grid(column=0, row=0)
    scr_path_e = c_ety(1, 1)
    scr_path_e.insert(0, scr_path)
    Label(config_frame, text="输入总文件夹的路径：").grid(column=0, row=1)
    scr_name_e = c_ety(1, 2)
    scr_name_e.insert(0, scr_name)
    Label(config_frame, text="输入这一次爬取的储存路径：").grid(column=0, row=2)

    config_save_btn = Button(config_frame, text="点此以保存配置", command=save_config)
    config_save_btn.grid(column=1, row=3)


def save_config():
    cookie_dict = {"cookie_path": cookie_path_e.get(), "scr_path": scr_path_e.get(), "scr_name": scr_name_e.get()}
    with open(r"config\config.txt", "w") as f:
        f.write(str(cookie_dict))
        f.close()

    scr_path_ = scr_path + scr_name + r"//"
    make_path(scr_path_)  # 先建立路径

    sl = Label(window, text="已保存！")
    sl.grid(column=1, row=4)


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

    with open(Path, "w") as f:
        for ID in ID_list:
            f.write(ID + "\n")
        f.close()

    Label(window, text="已导出").grid(column=7, row=4)


def c_ety(x, y):  # 创建新的输入框
    e = Entry(master=config_frame)
    e.grid(column=x, row=y)
    return e


class ConfigFrame:
    global config_frame, window
    config_frame = Frame(window, bd=20)
    config_frame.grid(column=1, row=0)
    config_setting()
    id_name_e = c_ety(2, 1)
    id_name_e.insert(0, "id_list")
    Label(config_frame, text="""在下方输入导出id时的文件名
路径同图片存储路径""").grid(column=2, row=0)
    export_id_btn = Button(config_frame, text="点此导出id", command=lambda: export_id(id_name_e=id_name_e))
    export_id_btn.grid(column=2, row=2)
