import jieba
import jieba.analyse
import pandas as pd
import sqlite3
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
jieba.set_dictionary(r'./jieba/dict.txt')
jieba.load_userdict(r'./jieba/user_dict.txt')

conn = sqlite3.connect(r'./lihkg.sqlite')
cur = conn.cursor()
cur.execute("SELECT title FROM lihkg_raw")
raw= cur.fetchall()


stop_word=open(r'./jieba/stop_word.txt',"r",encoding='utf-8')
stop_list=list()
for n in stop_word:
    stop_list.append(n.rstrip())


li = list()
for title in raw:
    title = str(title) #need to change thr format so that can be put in wordcloud
    seg_list = jieba.cut(title)
    for item in seg_list:
        if item in stop_list or item == " ":
            continue
        else:
            li.append(item)
wl=" ".join(li)

conn.commit()
cur.close()
stop_word.close()

user_input=input('Please input path of reference image for word cloud, leave it blank if NA: ')

if len(user_input)<1:
    mask_color = np.array(Image.open(r"./reference.png"))
else:
    mask_color = np.array(Image.open(user_input))

mask_color = mask_color[::3, ::3]
mask_image = mask_color.copy()
mask_image[mask_image.sum(axis=2) == 0] = 255
font_path= r"‪C:\Windows\Fonts\kaiu.ttf"
wordcloud = WordCloud(mask= mask_image,background_color="white", font_path=font_path, margin=2).generate(wl)

plt.imshow(wordcloud)
plt.axis("off")
plt.show()
wordcloud.to_file('test.png')

exit()
