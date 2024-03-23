from bs4 import BeautifulSoup as bs
import requests
import json

categories = {
    'Все рубрики': None,
    'Россия': 'russia',
    'Мир': 'world',
    'Бывший СССР': 'ussr',
    'Экономика': 'economics',
    'Силовые структуры': 'forces',
    'Наука и техника': 'science',
    'Спорт': 'sport',
    'Культура': 'culture',
    'Интернет и СМИ': 'media',
    'Ценности': 'style',
    'Путешествия': 'travel',
    'Из жизни': 'life',
    'Среда обитания': 'realty',
    'Забота о себе': 'wellness',
}


def get_news():
    news_date = input("За какой день хотите получить новости? (YYYY MM DD): ")
    rubric = input("Введите категорию: ")
    year, month, day = news_date.split()
    date_for_url = f"{year}/{month}/{day}"  # 2024/03/19
    date_for_json = f"{year}-{month}-{day}"  # 2024-03-19
    page_number = 1
    filtered_news = []
    while True:
        if not categories[rubric]:
            url = f'https://lenta.ru/{date_for_url}/page/{page_number}/'
        else:
            url = f'https://lenta.ru/rubrics/{categories[rubric]}/{date_for_url}/page/{page_number}/'
        page = requests.get(url)
        soup = bs(page.text, "html.parser")
        all_news = soup.find_all("li", class_='archive-page__item _news')
        page_number += 1
        if len(all_news) == 0:
            print('Новостей в данной категории больше нет.')
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

        if not categories[rubric]:
            with open(f'news_archive/{date_for_json}.json', 'w',
                      encoding='UTF-8') as file:
                json.dump(filtered_news, file, indent=4, ensure_ascii=False)
        else:
            with open(f'news_archive/{categories[rubric]}-{date_for_json}.json',
                      'w', encoding='UTF-8') as file:
                json.dump(filtered_news, file, indent=4, ensure_ascii=False)


def main():
    get_news()


if __name__ == '__main__':
    main()
