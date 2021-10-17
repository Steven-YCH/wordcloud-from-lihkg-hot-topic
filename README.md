# wordcloud_of_lihkg_hottopic
Generate wordcloud from lihkg hot topic

I am a new-learner of python & this is my first project aim to practice.

Lihkg is a popular forum in Hong Kong, these python code attempted to scrap lihkg hot topic & create wordcloud base on them.

Below library in python is involved
- sqlite3 (used for storing lihkg data)
- cloudscraper
- jieba (used for word analyse)

font "kaiu.ttf" is also involved to correctly show chinese in word cloud

lihkgspider.py
- run to scrap lihkg & store in sqlite3

analysekeyword.py
- run to create wordcloud from all topics stored in lihkg.sqlite which created by lihkgspider.py
- wordcloud deefault using "reference.png" as the shape of output, you can input any the location of your preferred image to change the shape of output

revising_userdict.py
- jieba default dictionary is used for words tokenizing, you can add your own words by running this program

revising_exceptdict.py
- you can exclude specific words by running this program

Sample of output
![test](https://user-images.githubusercontent.com/85422707/137614391-d0610115-c884-404b-9562-30cae9115b24.png)
