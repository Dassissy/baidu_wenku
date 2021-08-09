from tkinter import Tk, Label, Entry, Button, Frame
from web_crawler import main as web_crawler, make_path
from web_crawler import get_info
import time


window = Tk()
window.title("爬虫图形界面")
window.geometry("1000x400")

f = Frame(bd=20)

window.mainloop()