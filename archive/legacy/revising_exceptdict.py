#-*- coding:utf-8 -*-
stop_word=open(r'./jieba/stop_word.txt',"a",encoding='utf-8')
while True:
    user_input=input('Please input word for blocking, leave it blank for exiting: ')
    if len(user_input) < 1:
        break
    else:
        stop_word.write(user_input+'\n')
stop_word.close()
