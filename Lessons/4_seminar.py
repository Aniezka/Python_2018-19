#import requests
#import re

# скачиваем html-код страницы с помощью result.get
#result = requests.get('http://darkside.ru/show/')

# вытаскиваем из кода с помощью регулярки названия групп
#big_links = re.compile("<font class='titleshow'>.*?</font>", flags= re.DOTALL)
#titles = big_links.findall(result.text)

#new_titles = []
#regTag = re.compile('<.*?>', re.DOTALL)
#regSpace = re.compile('\s{2,}', re.DOTALL)
#for t in titles:
 #   clean_t = regSpace.sub("", t)
  #  clean_t = regTag.sub("", clean_t)
   # new_titles.append(clean_t)
#for t in new_titles:
 #   print(t)




#достаем код страницы из браузера, если есть сопротивление
import requests
import re

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
}

result = requests.get('http://waitbutwhy.com', headers=headers)

big_links = re.compile("<div class='post right'>.*?</div>", flags= re.DOTALL)
titles = big_links.findall(result.text)

new_titles = []
regTag = re.compile('<.*?>', re.DOTALL)
regSpace = re.compile('\s{2,}', re.DOTALL)
for t in titles:
    clean_t = regSpace.sub("", t)
    clean_t = regTag.sub("", clean_t)
    new_titles.append(clean_t)
for t in new_titles:
    print(t)



