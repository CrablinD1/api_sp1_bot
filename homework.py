import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
logging.basicConfig(filename='homework.log', format='%(asctime)s %(message)s')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')

    if status is None or homework_name is None:
        logging.error('В ответе отсутствует ключ "status" или "homework_name"')
        return f'В ответе отсутствует ключ "status" или "homework_name"'
    if status != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, params=params, headers=headers)
    except requests.exceptions.RequestException as error:
        logging.error(f'Произошла ошибка: {error}')
        return {}
    return homework_statuses.json()


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(600)  # опрашивать раз в пять минут

        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
