#-*- coding:utf-8 -*-
user_dict=open(r'./jieba/user_dict.txt',"a",encoding='utf-8')
while True:
    user_input=input('Please input word for adding, leave it blank for exiting: ')
    if len(user_input) < 1:
        break
    else:
        user_dict.write(user_input+'\n')
stop_word.close()
