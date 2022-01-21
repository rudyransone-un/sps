import time
import logging
import sqlite3
import datetime

import requests
import schedule


from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
URL = 'https://steamcommunity.com/profiles/76561199002236170'

db = sqlite3.connect('db.sqlite3')


def get_html(session: requests.Session, url: str):
    try:
        response = session.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            ' AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/97.0.4692.71 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        })
        response.raise_for_status()

        return response.text
    except requests.exceptions.HTTPError as err:
        logger.exception(err)
        raise


def get_status(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    status = soup.find('div', {'class': 'profile_in_game_header'})

    return status.text


def get_name(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    username = soup.find('span', {'class': 'actual_persona_name'})

    return username.text


def save_staus(session, url):
    cursor = db.cursor()
    html = get_html(session, url)
    username = get_name(html)
    status = get_status(html)
    offset = datetime.timedelta(hours=3)
    datetime.timezone(offset, name='МСК')
    created_at = datetime.datetime.now()

    try:
        cursor.execute(
            'insert into users(username, status, createdAt) values (?, ?, ?)',
            (username, status, created_at)
        )
        db.commit()
    except Exception as err:
        logger.exception(err)
        raise


def main():
    logger.info('started')
    session = requests.Session()
    save_staus(session, URL)


if __name__ == '__main__':
    schedule.every(1).minutes.do(main)

    logger.info('for')
    while True:
        schedule.run_pending()
        time.sleep(1)