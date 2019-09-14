import os
import json
from flask import Flask
from flask import url_for, render_template, request, redirect

app = Flask(__name__)

colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta']
col_names = ['lang', 'gender'] + colors
languages = ['nor', 'dan', 'swe', 'isl', 'spa', 'fra', 'mol', 'cat', 'bel']
languages_scand = ['nor', 'dan', 'swe', 'isl']


def load_data():
    with open('data.csv', 'r', encoding='utf-8') as file:
        return file.read()


def write_data(line):
    with open('data.csv', 'a', encoding='utf-8') as file:
        if os.stat('data.csv').st_size == 0:
            file.write(', '.join(col_names).upper() + '\n')
        file.write(line + '\n')


@app.route('/')
def index():
    urls = {
        'Статистика': url_for('stats'),
        'json': url_for('get_json'),
        'Поиск': url_for('search')
    }
    return render_template('index.html', urls=urls)


@app.route('/stats')
def stats():
    n_total = 0
    n_male = 0
    n_female = 0
    n_scand = 0

    lang_idx = dict(zip(languages, list(range(9))))

    n_lang = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for line in load_data().split('\n')[1:-1]:

        n_total += 1

        line_dict = dict(zip(col_names, line.split(', ')))

        if line_dict['lang']:
            n_lang[lang_idx[line_dict['lang']]] += 1
            if line_dict['lang'] in languages_scand:
                n_scand += 1

        if line_dict['gender'] == 'male':
            n_male += 1
        elif line_dict['gender'] == 'female':
            n_female += 1

    perc_lang = [n / n_total * 100 for n in n_lang]

    n_list = [n_total] + [n_male] + [n_female] + n_lang + [n_scand]
    perc_list = [100, n_male / n_total * 100,
                 n_female / n_total * 100] + perc_lang + [n_scand / n_total]

    return render_template('stats.html', n_list=n_list, perc_list=perc_list,
                           languages=languages)


@app.route('/json')
def get_json():
    csv_data = load_data()
    total_list = [dict(zip(col_names, line.split(', '))) for line in
                  csv_data.split('\n')[1:-1]]
    json_data = json.dumps(total_list)
    return render_template('json.html', json_data=json_data)


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/search_result')
def search_result():
    if request.args:
        search_color = request.args['search_color']

        if search_color not in colors:
            return render_template('search_result.html',
                                   lines_list=['Поиск не дал результатов'])

        search_result_list = ['Результаты поиска для цвета ' + search_color +
                              ':', 'GENDER, LANG, WORD']

        for line in load_data().split('\n')[1:-1]:

            line_dict = dict(zip(col_names, line.split(',')))

            if line_dict[search_color]:

                if 'search_scand' in request.args and line_dict['lang'] \
                        not in languages_scand:
                    continue

                search_result_list.append(', '.join([line_dict['gender'],
                                                     line_dict['lang'],
                                                     line_dict[search_color]]))

        return render_template('search_result.html',
                               lines_list=search_result_list)

    return render_template('search.html')


@app.route('/thanks')
def thanks():
    if request.args:

        lang = ''

        for now_lang in languages:
            if now_lang in request.args:
                lang = now_lang
                break

        gender = ''

        for now_gender in ['male', 'female']:
            if now_gender in request.args:
                gender = now_gender
                break

        color_list = []

        for color in colors:
            color_list.append(request.args[color])

        if not color_list:
            return redirect(url_for('index'))

        write_data(', '.join([lang] + [gender] + color_list))

        return render_template('thanks.html')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)