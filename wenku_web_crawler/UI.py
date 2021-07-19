from tkinter import Tk, Label, Frame, Entry, Button
from web_crawler import main as web_crawler
from web_crawler import get_info
import time

def ety(x,y):#创建新的输入框
    e = Entry(window)
    e.grid(column=x, row=y)
    return e
    
def save(e,y):#保存程序
    txt = e.get()
    #print("e.winfo_geometry() is:{}".format(e.winfo_geometry()))
    id_list[y-1] = txt#可修改
    try:
        title, num_of_pages = get_info(txt)#若id出错，这一步会报错
        l = Label(window, text="已保存:"+title+" : "+num_of_pages+"页")
        l.grid(column=2, row=y)
        
        if len(es_dict[e]) == 2:
            es_dict[e].append(title)
            es_dict[e].append(num_of_pages)
        else:
            es_dict[e][2] = title
            es_dict[e][3] = num_of_pages
        
        try:
            if error_l:#如果有出错信息存在
                error_l.grid_forget()#那就删了
        except:
            pass
        
    except:
        if txt == '':
            id_list[y-1] = ''
            l = Label(window, text="未检测到id！！")
            l.grid(column=2, row=y)
        else:
            id_list[y-1] = ''
            l = Label(window, text="id出错了！！")
            l.grid(column=2, row=y)
def save_btn(e,x,y):
    save_btn = Button(window, text="这是第"+str(y)+"个空：点击以保存", command = lambda : save(e,y))
    save_btn.grid(column=x, row=y)
    return save_btn
    
def CONTINUE(x,y,y_btn,finish_btn):
    id_list.append('')
    y_btn.destroy()
    finish_btn.destroy()
    try:
        f_l.grid_forget()
    except:
        pass
    entry_entry(x,y)
def BEGIN(x,y):
    global error_l, time_label#出错信息全局共享，时间信息方便删
    f_l.grid_forget()
    #print("id_list is:{}".format(id_list))
    
    for e in es_dict:#先进行保存
        if len(es_dict[e]) == 2:#如果没有启动过保存程序
            y = es_dict[e][1]
            save(e,y)
            
    ID_list = []#先删除出错id
    for ID in id_list:
        if not ID == '':
            ID_list.append(ID)
    if ID_list:
        try:
            time_label.grid_forget()
        except:
            pass
        
        time_start = time.time()#记录耗时
        scr_path_ = scr_path + scr_name + r"//"
        web_crawler(ID_list,scr_path_,cookie_path)#启动爬虫
        time_end = time.time()
        TIME = time_end - time_start
        
        f_l.grid(column=x, row=y+3)
        time_label = Label(window, text="耗时： "+str(TIME)+" 秒")
        time_label.grid(column=x+1, row=y+3)
    
    else:#如果此列表全空，那么就是所有的id都出错了
        error_l = Label(window, text="所有的id都出错了，请在更改后重试！！")
        error_l.grid(column=x, row=y+3)
    
def yes_btn(x,y):
    global f_l
    f_l = Label(window, text="爬虫已启动")
    finish_btn = Button(window, text="开始爬取", command = lambda : BEGIN(x,y))
    finish_btn.grid(column=x, row=y)
    y_btn = Button(window, text="要继续吗？", command = lambda : CONTINUE(x,y,y_btn,finish_btn))
    y_btn.grid(column=x+1, row=y)
    
def export_id(id_name_e):
    if id_name_e.get():
        id_name = id_name_e.get()
    else:
        id_name = "id_list"
    
    Path = scr_path + scr_name + "//" + id_name + ".txt"
    
    ID_list = []#先删除出错id
    for ID in id_list:
        if not ID == '':
            ID_list.append(ID)
            
    with open(Path, "w") as f:
        for ID in ID_list:
            f.write(ID+"\n")
        f.close()
        
    Label(window, text="已导出").grid(column=7,row=4)
    
def entry_entry(x,y):
    global es_dict,id_list#全局化
    e = ety(x,y)
    s_btn = save_btn(e,x+1,y)
    
    config_setting()
    
    Label(window, text="""在下方输入导出id时的文件名
路径同图片存储路径""").grid(column=7,row=1)
    id_name_e = ety(7,2)
    id_name_e.insert(0,"id_list")
    export_id_btn = Button(window, text="点此导出id",command=lambda:export_id(id_name_e))
    export_id_btn.grid(column=7,row=3)
    
    es_dict[e] = [s_btn,y]
    
    yes_btn(x,y+1)#由于使用了递归结构，此处传入y+1可看作是y+=1
    
def config_setting():
    global cookie_path_e, scr_path_e, scr_name_e,cookie_path,scr_path,scr_name#配置全局化
    with open(r"config\config.txt","r+") as f:#读写配置
        config_dict = eval(f.read())
    cookie_path = config_dict["cookie_path"]
    scr_path = config_dict["scr_path"]
    scr_name = config_dict["scr_name"]
    
    cookie_path_e = ety(6,1)
    cookie_path_e.insert(0, cookie_path)
    Label(window,text="输入cookie的路径：").grid(column=5,row=1)
    scr_path_e = ety(6,3)
    scr_path_e.insert(0, scr_path)
    Label(window,text="输入总文件夹的路径：").grid(column=5,row=3)
    scr_name_e = ety(6,4)
    scr_name_e.insert(0, scr_name)
    Label(window,text="输入这一次爬取的储存路径：").grid(column=5,row=4)
    
    config_save_btn = Button(window, text="点此以保存配置",command=save_config)
    config_save_btn.grid(column=6,row=6)
    
def save_config():
    cookie_dict = {}
    cookie_dict["cookie_path"] = cookie_path_e.get()
    cookie_dict["scr_path"] = scr_path_e.get()
    cookie_dict["scr_name"] = scr_name_e.get()
    with open(r"config\config.txt","w") as f:
        f.write(str(cookie_dict))
        f.close()
    Label(window,text="已保存！").grid(column=6,row=7)

def main(x,y):
    entry_entry(x,y)
    window.mainloop()

window = Tk()
window.title("爬虫图形界面")
window.geometry("1000x400")

l1 = Label(window, text="在下方的框内输入id")
l1.grid(column=0, row=0)

es_dict = {}#输入框和输入信息的字典
id_list = ['']#第一个空的初始化
x=0
y=1
main(x,y)
    
