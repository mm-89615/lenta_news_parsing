from bs4 import BeautifulSoup as bs
import requests
import json


url = 'https://lenta.ru/2024/03/19/'

page = requests.get(url)

filtered_news = []
all_news = []

soup = bs(page.text, "html.parser")

all_news = soup.find_all("li", class_='archive-page__item _news')


def get_news():
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
    get_news()


if __name__ == '__main__':
    main()
