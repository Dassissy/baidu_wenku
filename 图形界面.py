from tkinter import Tk, Label, Frame, Entry, Button
  
def ety(x,y):#创建新的输入框
    e = Entry(window)
    e.grid(column=x, row=y)
    return e
    
def save(e,y):#保存程序
    txt = e.get()
    #print("e.winfo_geometry() is:{}".format(e.winfo_geometry()))
    #Y = (int(e.winfo_geometry().split("+")[-1])+3)//30
    #print("Y is:{}".format(Y))
    #print("y is:{}".format(y))
    #Y永远==y，下方代码无意义，故注释化
    #if Y == y:
        #id_list.append(txt)
    id_list[y-1] = txt#可修改
    l = Label(window, text="已保存:"+txt)
    l.grid(column=2, row=y)
def btn(e,x,y):
    btn = Button(window, text="这是第"+str(y)+"个空：点击以保存", command = lambda : save(e,y))
    btn.grid(column=x, row=y)
    
def CONTINUE(x,y,y_btn,finish_btn):
    id_list.append('')
    y_btn.destroy()
    finish_btn.destroy()
    entry_entry(x,y)
def BEGIN(x,y,f_l,id_list):
    f_l.grid_forget()
    f_l.grid(column=x, row=y+3)
    #print("id_list is:{}".format(id_list))
    pass
def yes_btn(x,y):
    f_l = Label(window, text="暂时还没有搭载上爬虫")
    finish_btn = Button(window, text="开始爬取", command = lambda : BEGIN(x,y,f_l,id_list))
    finish_btn.grid(column=x, row=y)
    y_btn = Button(window, text="要继续吗？", command = lambda : CONTINUE(x,y,y_btn,finish_btn))
    y_btn.grid(column=x+1, row=y)
    
def entry_entry(x,y):
    e = ety(x,y)
    btn(e,x+1,y)
    yes_btn(x,y+1)#由于使用了递归结构，此处传入y+1可看作是y+=1
    
    
def main(x,y):
    entry_entry(x,y)
    window.mainloop()

window = Tk()
window.title("爬虫图形界面")
window.geometry("400x400")

l1 = Label(window, text="在下方的框内输入id")
l1.grid(column=0, row=0)

id_list = ['']#第一个空的初始化
x=0
y=1
main(x,y)
    
