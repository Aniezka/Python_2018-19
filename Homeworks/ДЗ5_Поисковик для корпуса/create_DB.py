import sqlite3
import os


def create_database():
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS articles(path text, author text,\
        header text, date text, plain_text text, mystem_plain text)')

    with open(os.path.join('Газета', 'metadata.csv'), 'r', encoding='utf-8')\
            as file:
        metadata = file.read().split('\n')

    for line in metadata:

        line_list = line.split('\t')
        path = line_list[0]
        author = line_list[1]
        header = line_list[2]
        date = line_list[3]
        dd, mm, yyyy = date.split('.')

        # print(path, author, header, dd, mm, yyyy)

        with open(os.path.join('Газета', 'plain', yyyy, mm, header + '.txt'),
                  'r', encoding='utf-8') as file:
            plain_text = file.read()

        with open(os.path.join('Газета', 'mystem-plain', yyyy, mm,
                               header.replace(' ', '_') + '.txt'),
                  'r', encoding='utf-8') as file:
            mystem_plain = file.read()

        # print(plain_text)
        # print(mystem_plain)

        c.execute('INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?)',
                  (path, author, header, date, plain_text, mystem_plain))

        conn.commit()

    conn.close()


if __name__ == '__main__':
    create_database()
