from bs4 import BeautifulSoup as bs
import requests
import json
import os

categories = {
    "Все рубрики": None,
    "Россия": "russia",
    "Мир": "world",
    "Бывший СССР": "ussr",
    "Экономика": "economics",
    "Силовые структуры": "forces",
    "Наука и техника": "science",
    "Спорт": "sport",
    "Культура": "culture",
    "Интернет и СМИ": "media",
    "Ценности": "style",
    "Путешествия": "travel",
    "Из жизни": "life",
    "Среда обитания": "realty",
    "Забота о себе": "wellness",
}


def get_news(date: str, rubric: str, chat_id: int) -> None:
    """
    Принимает на вход день новостей, категорию и чат айди.
    Собирает новости с сайта LENTA.ru.

    :param date: День новостей
    :param rubric: Категория новсетей имеющихся на сайте
    :param chat_id: Чат айди пользователя. Необходим для создания json
                    файла с именем = id
    :return:
    """
    # Преобразует дату в необходимый формат для URL
    year, month, day = date.split("-")
    date_for_url = f"{year}/{month}/{day}"  # 2024/03/19
    page_number = 1
    filtered_news = []
    # Удаляет json файл, если он есть.
    if os.path.exists(f'received_news/{chat_id}.json'):
        os.remove(f'received_news/{chat_id}.json')

    while True:
        # Определяет какая ссылка будет использоваться для парсинга
        if not categories[rubric]:
            url = f"https://lenta.ru/{date_for_url}/page/{page_number}/"
        else:
            url = (f"https://lenta.ru/rubrics/{categories[rubric]}/"
                   f"{date_for_url}/page/{page_number}/")
        page = requests.get(url)
        soup = bs(page.text, "html.parser")
        # все новости на конкретной странице
        all_news = soup.find_all("li", class_="archive-page__item _news")
        page_number += 1
        # перестает парсить если больше на странице не нашлось новостей
        if len(all_news) == 0:
            break
        # создание отдельного словаря для каждой новости
        for data in all_news:
            title_news = data.find("h3", class_="card-full-news__title")
            publication_time = data.find(
                "time",
                class_="card-full-news__info-item card-full-news__date"
            )
            category_news = data.find(
                "span",
                class_="card-full-news__info-item card-full-news__rubric"
            )
            url = data.find("a", href=True)
            # словарь с конкретной новостью
            news = {
                "title": title_news.text,
                "publication_time": publication_time.text,
                "category": category_news.text,
                "url": "https://lenta.ru" + url["href"],
            }
            # добавление новости в общий список
            filtered_news.append(news)
        # запись всех новостей в json файл
        with open(f"received_news/{chat_id}.json", "w",
                  encoding="UTF-8") as file:
            json.dump(filtered_news, file, indent=4, ensure_ascii=False)
