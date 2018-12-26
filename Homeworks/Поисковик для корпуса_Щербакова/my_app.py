import os
from flask import Flask
from flask import url_for, render_template, request, redirect
import sqlite3
import re

app = Flask(__name__)


search_query = ''
search_result_list = ''


def get_search_result(now_search_query):

    conn = sqlite3.connect('articles.db')
    c = conn.cursor()

    search_re_in = re.compile(r'[а-я]+', flags=re.IGNORECASE)
    search_in_result = search_re_in.findall(now_search_query)

    with open('mystem_input.txt', 'w', encoding='utf-8') as in_file:
        in_file.write(' '.join(search_in_result))

    os.system('./mystem -l mystem_input.txt mystem_output.txt')

    with open('mystem_output.txt', 'r', encoding='utf-8') as out_file:
        out_content = out_file.read()

    search_re_out = re.compile(r'{([а-я]+)[}|]', flags=re.IGNORECASE)
    search_list = search_re_out.findall(out_content)
    mystem_plain_re = re.compile(r'{([а-я]+)=', flags=re.IGNORECASE)
    search_result = []

    for row in c.execute('SELECT path, header, plain_text,'
                         'mystem_plain FROM articles'):
        path, header, plain_text, mystem_plain = row
        mystem_words_list = mystem_plain_re.findall(mystem_plain)
        text_len = 0
        found = False

        for i in range(len(mystem_words_list) - len(search_list)):
            if found:
                break

            matches = 0

            for j in range(len(search_list)):

                if mystem_words_list[i + j] == search_list[j]:
                    matches += 1

                    if matches == len(search_list):
                        if i < 10:
                            beg_ind = 0
                        else:
                            beg_ind = i - 10

                        if i + 50 >= len(plain_text):
                            end_ind = len(plain_text)
                        else:
                            end_ind = i + 60

                        plain_text_fragment = \
                            ' '.join(plain_text.split(' ')[beg_ind:end_ind]) \
                            .replace('\xa0', '').replace('\u202f', '')
                        search_result.append([path, header, '...' +
                                              plain_text_fragment + '...'])
                        found = True

            text_len += len(mystem_words_list[i])
    conn.close()

    return search_result


@app.route('/')
def index():

    if not request.args:
        return render_template('index.html', is_result=False)

    if 'search_query' in request.args:

        global search_query
        search_query = request.args['search_query']
        global search_result_list
        search_result_list = get_search_result(search_query)

    print(search_result_list)

    now_page = 0

    print(request.args)

    if 'now_page' in request.args:
        now_page = int(request.args['now_page']) - 1

    results_on_page = 20

    n_pages = len(search_result_list) // results_on_page

    if now_page > n_pages - 1 or now_page < 0:
        now_page = 0

    pages_before = ' '.join(map(str, list(range(1, now_page + 1))))
    pages_after = ' '.join(map(str, list(range(now_page + 2, n_pages + 1))))

    pages = pages_before + ' (' + str(now_page + 1) + ') ' + pages_after

    ind_beg = now_page * results_on_page
    ind_end = (now_page + 1) * results_on_page

    keys = list(range(ind_beg + 1, ind_end + 1))
    values = search_result_list[ind_beg:ind_end]

    now_search_result_dict = dict(zip(keys, values))

    is_empty = True
    if len(now_search_result_dict) > 0:
        is_empty = False

    return render_template('index.html',
                           is_result=True,
                           search_query=search_query,
                           now_search_result_dict=now_search_result_dict,
                           n_pages=n_pages, now_page=now_page + 1,
                           pages=pages, is_empty=is_empty)


if __name__ == '__main__':
    app.run(debug=True)
