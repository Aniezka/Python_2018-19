import urllib.request
import json
import re
from pymystem3 import Mystem
import sqlite3
import operator
import matplotlib.pyplot as plt
from flask import Flask
from flask import render_template
import os

token = os.environ["TOKEN"]

owner_id1 = -94208167  # Data Mining
owner_id2 = -91453124  # Data Science
owner_id3 = -49815762  # Data Mining Labs

table1 = 'data_mining'
table2 = 'data_science'
table3 = 'data_mining_labs'

a = 'https://api.vk.com/method/'
b = 'wall.get?'
c = 'owner_id=%i&offset=%i&count=%i&v=5.92&access_token=%s'

d1 = 'data_unlemmatized_'
d2 = 'data_lemmatized_'

conn = sqlite3.connect('final_project_data.db')
c1 = conn.cursor()


def get_posts(how_many, id_local):
        count = 0
        r = how_many % 100
        local_posts = {}
        i = 0
        while i < how_many//100:
            p1 = a + b + c
            req = urllib.request.Request(p1 % (id_local, 100*i, 100, token))
            response = urllib.request.urlopen(req)
            result = response.read().decode('utf-8')
            data1 = json.loads(result)
            data_length = len(data1['response']['items'])

            for j in range(min(100, data_length)):
                local_posts[j+100*i] = data1['response']['items'][j]

            count = i + 1
            i = i + 1
            if data_length < 100:
                i = how_many
                r = 0

        if r > 0:
            p2 = a + b + c
            req = urllib.request.Request(p2 % (id_local, 100*count, r, token))
            response = urllib.request.urlopen(req)
            result = response.read().decode('utf-8')
            data1 = json.loads(result)

            for i in range(r):
                local_posts[i+100*count] = data1['response']['items'][i]

        return local_posts


def save_posts_data_to_database(posts_local, table):
    file_for_rewriting = open(d1 + table + '.txt', 'w', encoding='utf-8')
    file_for_rewriting.write('')
    file_for_rewriting.close()

    file_local = open(d1 + table + '.txt', 'a', encoding='utf-8')

    s1 = 'INSERT INTO ' + table + ' VALUES (?, ?)'
    for i in range(len(posts_local)):
        post_id = posts_local[i]['id']
        text = posts_local[i]['text']
        file_local.write(text + '\n')
        c1.execute(s1, (post_id, text))
        conn.commit()

    file_local.close()


def save_lemmatized_data(texts_local, table):
    m = Mystem()
    file_local = open(d2 + table + '.txt', 'w', encoding='utf-8')
    file_local.write('')
    file_local.close()

    file_local = open(d2 + table + '.txt', 'a', encoding='utf-8')
    text = ''
    count = 0
    for line_local in texts_local.split('\n'):
        text = text + line_local + ' '
        if count > 10:
            lemma = m.lemmatize(text)
            file_local.write(''.join(lemma))
            text = ''
            count = 0
        count += 1

    lemma = m.lemmatize(text)
    file_local.write(''.join(lemma))
    file_local.close()


def get_stop_words_from_file(file_local):
    stop_words = list([])
    f = open(file_local, 'r', encoding='utf-8')
    f1 = f.readlines()
    for x in f1:
        stop_words.append(x.split('\n')[0])

    return stop_words


def get_top_words_from_file(file_local):
    top_words = list([])
    f = open(file_local, 'r', encoding='utf-8')
    f1 = f.readlines()
    for x in f1:
        top_words.append(x.split('\n')[0])

    return top_words


def get_data_from_file(table):
    file_local_1 = open(d1 + table + '.txt', 'r', encoding='utf-8')
    texts_local = file_local_1.read()
    file_local_1.close()

    return texts_local


def get_top_number_words_lemmatized(how_many, table, color_local):
    file_local = open(d2 + table + '.txt', "r", encoding='utf-8')
    texts_local = file_local.read()
    file_local.close()
    stop_words = get_stop_words_from_file('stop_ru.txt')
    top_words = get_top_words_from_file('top_words_' + table + '.txt')
    words_count = dict()
    words = re.compile('\w+').findall(texts_local.lower())

    for word in words:
        if word not in stop_words and word in top_words:
            if words_count.get(word) is None:
                words_count[word] = 1
            else:
                words_count[word] += 1

    ky = operator.itemgetter(1)
    words_count1 = sorted(words_count.items(), key=ky, reverse=True)
    words_top = list([])
    X = list([])
    Y = list([])

    for m in range(min(how_many, len(words_count1))):
        words_top.append(words_count1[m][0])
        X.append(m + 1)
        Y.append(words_count1[m][1])

    plt.bar(X, Y, color=color_local)
    plt.title("Ключевые слов")
    plt.xlabel("Слова")
    plt.ylabel("Частотность слов")
    plt.xticks(X, words_top, rotation=75)
    plt.subplots_adjust(bottom=0.3)
    plt.savefig('static/img/' + table + '.png')
    plt.clf()

    return X, Y


def get_comparison_graph(x, y_1, y_2, y_3):
    plt.plot(x, y_1, color='#89a203')
    plt.plot(x, y_2, color='#96f97b')
    plt.plot(x, y_3, color='#029386')

    lines = list()
    lines.append('Data Mining | Анализ данных')
    lines.append('Data Science')
    lines.append('Data Mining Labs')
    plt.legend(lines)

    s1 = 'График-сравнение частотности 18 самых '
    s2 = 'частотных ключевых слов по трем сообществам'
    plt.title(s1 + s2)

    plt.xlabel("Рейтинг слов")
    plt.ylabel("Частотность слов")
    plt.xticks(x)
    plt.subplots_adjust(bottom=0.1)

    fig = plt.gcf()
    fig.set_size_inches(9, 5)

    plt.savefig('static/img/' + 'comparison_graph' + '.png', dpi=100)
    plt.clf()


def rewrite_all_data_and_run(how_many):
    c1.execute('DROP TABLE IF EXISTS data_mining')
    c1.execute('DROP TABLE IF EXISTS data_science')
    c1.execute('DROP TABLE IF EXISTS data_mining_labs')

    s1 = 'CREATE TABLE IF NOT EXISTS '
    pq1 = s1 + 'data_mining(post_id integer, text text)'
    pq2 = s1 + 'data_science(post_id integer, text text)'
    pq3 = s1 + 'data_mining_labs(post_id integer, text text)'

    c1.execute(pq1)
    c1.execute(pq2)
    c1.execute(pq3)

    posts1 = get_posts(how_many, owner_id1)  # WARNING!!!
    posts2 = get_posts(how_many, owner_id2)  # WARNING!!!
    posts3 = get_posts(how_many, owner_id3)  # WARNING!!!

    save_posts_data_to_database(posts1, table1)  # WARNING!!!
    save_posts_data_to_database(posts2, table2)  # WARNING!!!
    save_posts_data_to_database(posts3, table3)  # WARNING!!!

    save_lemmatized_data(get_data_from_file(table1), table1)  # WARNING!!!
    save_lemmatized_data(get_data_from_file(table2), table2)  # WARNING!!!
    save_lemmatized_data(get_data_from_file(table3), table3)  # WARNING!!!


# rewrite_all_data_and_run(300)

x1, y1 = get_top_number_words_lemmatized(40, table1, '#89a203')
x2, y2 = get_top_number_words_lemmatized(40, table2, '#96f97b')
x3, y3 = get_top_number_words_lemmatized(40, table3, '#029386')

get_comparison_graph(x1, y1, y2, y3)

app = Flask(__name__)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response


@app.route('/')
def welcome_page():
    return render_template('welcome_page.html')


@app.route('/data_mining')
def gdata_mining_page():
    return render_template('data_mining_page.html')


@app.route('/data_science')
def data_science_page():
    return render_template('data_science_page.html')


@app.route('/data_mining_labs')
def data_mining_labs_page():
    return render_template('data_mining_labs_page.html')


@app.route('/comparison')
def comparison_page():
    return render_template('comparison_page.html')


'''
if __name__ == '__main__':
    app.run(debug=False)
'''

if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

conn.close()
