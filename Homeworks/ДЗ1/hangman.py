import random
import re

# можно ввести с новой строки одну букву русского алфавита, заканчивается концом строки
VALID_RE = re.compile('^[а-я]$')

# рисует нужную "часть" человека
def print_hangman(attempts):

    str_list = ['|----',
                '|  | ',
                '|  o ',
                '| /|\\',
                '| / \\',
                '|      '
                ]

 #делаем перевод строчки
    print('\n'.join(str_list[attempts:]))


def get_word_list():

 # то, во что будем записывать имя файла, который нужно открыть
    filename = ''

    while not filename:

        print('Выберите категорию:\nКотики, Песики, Курочки')
        cat = input()

        if cat == 'Котики':
            filename = 'cats.txt'

        elif cat == 'Песики':
            filename = 'dogs.txt'

        elif cat == 'Курочки':
            filename = 'hens.txt'

        else:
            print('Неверная категория!\n')

    with open(filename, 'r', encoding='utf-8') as textfile:

        word_list = textfile.read().split()

    return word_list


def play_the_game(word):

    while True:

        print('\n##############')
        print('# Новая игра #')
        print('##############')

        guessed_letters = []
        attempts = 6

        while attempts:

            print('Попыток:', attempts)
            now_state = []

            for letter in word:

                if letter in guessed_letters:
                    now_state.append(letter)
                else:
                    now_state.append('_')

            print('Слово:', ' '.join(now_state))

            input_letter = input('Введите букву: ').strip().lower()

            if not VALID_RE.match(input_letter):
                print('Неверный формат ввода!\n')
                continue

            if input_letter in guessed_letters:
                print('Букву {} Вы уже угадали\n'.format(input_letter))
                continue

            if input_letter in word:

                print('Верная буква\n')

                guessed_letters.append(input_letter)

                if len(guessed_letters) == len(set(word)):
                    break

                continue

            else:
                print('Неверная буква\n')

            attempts -= 1
            print_hangman(attempts)

        if attempts:
            print('Вы выиграли')

        else:
            print('Вы проиграли')

        ans = input('\nПродолжить? [Y/n]: ')

        while ans not in ['', 'Y', 'y', 'N', 'n']:
            ans = input('\nПродолжить? [Y/n]: ')

        if ans in ['n', 'N']:
            break


def main():

    word_list = get_word_list()
    play_the_game(random.choice(word_list).lower())


if __name__ == '__main__':
    import sys

    sys.exit(main())