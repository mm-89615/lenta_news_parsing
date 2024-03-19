from bs4 import BeautifulSoup as bs
import requests
import json
import sqlite3
from sqlite3 import Error


def get_news_db():
    connection = sqlite3.connect("news_db.db")
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
    title TEXT,
    time datetime,
    category TEXT,
    url TEXT
    )
    ''')
    # cursor.execute('CREATE INDEX idx_title ON news (title)')
    cursor.execute("DELETE FROM news")
    page_number = 1
    filtered_news = []
    while True:

        url = f'https://lenta.ru/2024/03/19/page/{page_number}/'
        page = requests.get(url)
        soup = bs(page.text, "html.parser")
        all_news = soup.find_all("li", class_='archive-page__item _news')
        page_number += 1
        if len(all_news) == 0:
            break
        else:
            for data in all_news:
                title_news = data.find(
                    'h3',
                    class_='card-full-news__title')
                publication_time = data.find(
                    'time',
                    class_='card-full-news__info-item card-full-news__date')
                category_news = data.find(
                    'span',
                    class_='card-full-news__info-item card-full-news__rubric')
                url = data.find('a', href=True)

                news = {
                    'title': title_news.text,
                    'publication_time': publication_time.text,
                    'category': category_news.text,
                    'url': "https://lenta.ru" + url['href']
                }
                cursor.execute(
                    'INSERT INTO news (title, time, category, url) VALUES (?, ?, ?, ?)',
                    (title_news.text, publication_time.text, category_news.text,
                     ("https://lenta.ru" + url['href'])))

    connection.commit()
    connection.close()


def get_news():
    page_number = 1
    filtered_news = []
    while True:

        url = f'https://lenta.ru/2024/03/19/page/{page_number}/'
        page = requests.get(url)
        soup = bs(page.text, "html.parser")
        all_news = soup.find_all("li", class_='archive-page__item _news')
        page_number += 1
        if len(all_news) == 0:
            break
        else:
            for data in all_news:
                title_news = data.find(
                    'h3',
                    class_='card-full-news__title')
                publication_time = data.find(
                    'time',
                    class_='card-full-news__info-item card-full-news__date')
                category_news = data.find(
                    'span',
                    class_='card-full-news__info-item card-full-news__rubric')
                url = data.find('a', href=True)

                news = {
                    'title': title_news.text,
                    'publication_time': publication_time.text,
                    'category': category_news.text,
                    'url': "https://lenta.ru" + url['href']
                }

                filtered_news.append(news)

        with open('filtered_news.json', 'w', encoding='UTF-8') as file:
            json.dump(filtered_news, file, indent=4, ensure_ascii=False)


def main():
    # get_news()
    get_news_db()


if __name__ == '__main__':
    main()
