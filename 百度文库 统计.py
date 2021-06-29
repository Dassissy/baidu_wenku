# -*- coding: utf-8 -*-
"""
Created on Sat May 29 16:34:31 2021

@author: Administrator
"""
import os,re
import matplotlib.pyplot as plt
import numpy as np

def pie(input_dict,others=True,others_list=[],others_quantity=0,del_list=[]):
    if others:
        ALL = 0
        for i in input_dict.values():
            ALL += i
            
        try:
            others_threshold = 0.02
        except ZeroDivisionError:
            print("无")
            return 0
            
        for key in input_dict:
            #print("value = {},\nALL = {}\nvalue/ALL = {}".format(input_dict[key],ALL,input_dict[key]/ALL))
            if input_dict[key]/ALL <= others_threshold:
                others_quantity += input_dict[key]
                others_list.append(key)
                del_list.append(key)
        
        #print("others is:{}".format(others_list))
        for i in del_list:
            del input_dict[i]  
            input_dict["OTHERS"] = others_quantity
        others_list.clear()
        del_list.clear()
    key_list = []
    count_list = []
    for key in input_dict:
        key_list.append(key)
        count_list.append(input_dict[key])
    
    #print(("letter_list, count_list are:\n{}, \n{}").format(letter_list,count_list))
    
    labels = key_list
    sizes = count_list
    # explode = (0, 0, 0, 0)
    
    fig1, ax1 = plt.subplots()
    a, l, p = ax1.pie(sizes,labels=labels, autopct='%1.1f%%', startangle=90)
    #print(("a, l, p are:{}, {}, {}").format(a,l,p))
    for t in l:
        t.set_size(9)
    for t in p:
        t.set_size(9)
    
    ax1.axis('equal') 
    plt.rcParams['figure.figsize'] = (7, 5)
    plt.rcParams['savefig.dpi'] = 100
    plt.rcParams['figure.dpi'] = 100
    plt.show()

def bar(input_dict):
    label_list = []
    quantity_list = []
    for label in input_dict:
        label_list.append(label)
        quantity_list.append(input_dict[label])
    
    x = np.arange(len(label_list))  # the label locations
    width = 0.4  # the width of the bar
    fig, ax = plt.subplots()
    ax.bar(x - width/2, quantity_list, width, label='Quantity')
    ax.set_ylabel('Quantity')
    ax.set_title('English words census')
    ax.set_xticks(x)
    ax.set_xticklabels(label_list)
    ax.legend()
    
    fig.tight_layout()
    
    plt.show()
    
    
    ALL = 0
    for i in quantity_list:
        ALL += i
    for i in range(len(quantity_list)):
        quantity_list[i] = round(quantity_list[i]/ALL,2)
    fig, ax = plt.subplots()
    ax.bar(x - width/2, quantity_list, width, label='Frequency')
    
    ax.set_ylabel('Frequency')
    ax.set_title('English letters census')
    ax.set_xticks(x)
    ax.set_xticklabels(label_list)
    ax.legend()
    
    fig.tight_layout()
    
    plt.show()
    
    
def fix_txt(path):
    path_list = os.listdir(path)
    TXT = ''
    for p in path_list:
        Path = path + "\\" + p
        with open(Path, "r", encoding="utf-8") as f:
            txt = f.read()
            TXT = TXT + txt
    return TXT

def analyse(string):
    string = re.sub(r'[^a-zA-Z\n ]'," ",string)#删非字母的所有内容
    string = re.sub(r"[ ]{2,}"," ",string)#多于一个的空格要删掉
    string = re.sub(r'\n',' ',string).lower()#回车换成空格,顺便全部换成小写
    string = re.sub(r"[ ]{2,}"," ",string)#再删一遍
    #删除多次才有效果
    string = re.sub(r' \w ','  ',string) #删单个字母
    string = re.sub(r' \w ','  ',string) #删单个字母
    string = re.sub(r' \w ','  ',string) #删单个字母
    
    string = re.sub(r'[abcde]{5}'," ",string)#答案格式：abbac acdba ...
    
    string = re.sub(r"[ ]{2,}"," ",string)#再删一遍
    
    
    
    
    words_list = string.split(" ")
    words_copy = []#不重复地记录单词
    for word in words_list:
        if word not in words_copy:
            words_copy.append(word)
        else:
            continue
    word_count_dict = {}#单词出现次数
    for word in words_copy:
        word_count_dict[word] = words_list.count(word)
    del word_count_dict[""]#删去空字符串
    
    let = "abcdefghigklmnopqrstuvwxyz"
    let_list = list(let)#首字母列表
    let_count_dict = {}
    for let in let_list:
        let_count_dict[let] = 0#初始化首字母字典
        
    for let in let_list:
        for i in word_count_dict:
            if i == "the":
               continue
            if i[0] == let:
                let_count_dict[let] = let_count_dict[let] + word_count_dict[i]
            else:
                continue
            
    return word_count_dict, let_count_dict

def out(path, word_count_dict, let_count_dict):
    words_path = path + "\\word_count_dict.txt"
    let_path = path + "\\let_count_dict.txt"
    
    with open(words_path,"w") as f:
        f.write(str(word_count_dict))
    with open(let_path,"w") as f:
        f.write(str(let_count_dict))
    
path = input("输入待统计的文件夹的路径 ：")
if not path:
    path = "D:/阅读文件/10-11"
txt = fix_txt(path)
word_count_dict, let_count_dict = analyse(txt)
#按值从大到小排列
#sorted_dict_list = sorted(zip(let_count_dict.values(),let_count_dict.keys()),reverse=True)
#sorted_dict = {}
#for t in sorted_dict_list:
#    sorted_dict[t[1]] = t[0]

#bar(sorted_dict)
#out(path, word_count_dict, let_count_dict)



def root_find(root, word_count_dict):
    root_dict = {}
    pat = r".*?" + root + r".*?"
    for word in word_count_dict:
        if not re.match(pat, word) == None:
            root_dict[word] = word_count_dict[word]
    #for word in root_dict:
    #    print(word,":",root_dict[word])
    pie(root_dict)
        
def prefix_find(prefix, word_count_dict):
    prefix_dict = {}
    pat = "^" + prefix
    for word in word_count_dict:
        if not re.match(pat, word) == None:
            prefix_dict[word] = word_count_dict[word]
    #for word in prefix_dict:
    #    print(word,":",prefix_dict[word])
    pie(prefix_dict)
        
def postfix_find(postfix, word_count_dict):
    postfix_dict = {}
    pat =  r".*?" + postfix + "$"
    for word in word_count_dict:
        if not re.match(pat, word) == None:
            postfix_dict[word] = word_count_dict[word]
    #for word in postfix_dict:
    #    print(word,":",postfix_dict[word])
    pie(postfix_dict)
    
while True:
    try:
        choose = int(input("""查找词根请按1
查找前缀请按2
查找后缀请按3
退出请按4：
"""))
    except:
        print("请重新选择")
        continue
    if choose == 1:
        root = input("输入要查找的词根：")
        root_find(root, word_count_dict)
    elif choose == 2:
        prefix = input("输入要查找的前缀：")
        prefix_find(prefix, word_count_dict)
    elif choose == 3:
        postfix = input("输入要查找的后缀：")
        postfix_find(postfix, word_count_dict)
    elif choose == 4:
        break
    else:
        print("请重新选择")