import requests
from bs4 import BeautifulSoup

import logger as log


class Vk:
    def __init__(self):
        self.author = None
        self.link_post = None
        self.post_text = None

    def parse_main_page(self, url: str) -> tuple[BeautifulSoup, ...]:
        """Возвращает кортеж постов."""
        assert isinstance(url, str), f'{url} - ссылка должна быть строкой'
        self._get_page(url)
        # self._load_page("main")
        items = tuple(reversed(self.soup.find_all('div', class_='post')))
        assert len(items) == 10, f"{len(items)=}"
        self.author = self.soup.find('h1', class_='page_name').text
        assert self.author, "no author"
        return items

    def _get_page(self, url: str) -> None:
        """Возвращает soup страницы."""
        try:
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
            }
            request = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError as err:
            log.error(f"[ERROR] невозможно открыть ссылку {err}")
            raise requests.exceptions.ConnectionError(err)
        soup = BeautifulSoup(request.text, 'html.parser')
        self.soup = soup

    def save_page(self, name: str) -> None:
        """Сохранение страницы в файле."""
        with open(f"{name}.html", "w", encoding="utf-8") as file:
            file.write(str(self.soup))

    def _load_page(self, name: str) -> None:
        """Загружает, предварительно, скачанную страницу."""
        with open(f"{name}.html", 'r', encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
        self.soup = soup

    def get_post_id(self, item: BeautifulSoup) -> str:
        """Возвращает id поста."""
        post_id = item.get('id')
        return post_id

    def item_parse(self, item: BeautifulSoup) -> tuple[str, list[str, ...]] or None:
        """Возвращает данные из поста (текст поста, ссылки на медиа)."""

        self.link_post = 'https://vk.com' + item.find('a', class_='post_link').get('href')
        item_content = item.find("div", class_="wall_text")

        photos = item_content.find_all('a', {'aria-label': 'фотография'})
        gifs = item_content.find_all('a', {'class': 'page_doc_photo_href'})
        videos = item_content.find_all('div', class_="page_post_video_play_inline")

        post_text = self._get_text(item_content)

        copy_quote = item_content.find('div', class_='copy_quote')
        if copy_quote:
            author_copy = copy_quote.find('a', class_='copy_author').text
            post_text = f"{post_text}\nРЕПОСТ: {author_copy}\n\n{self._get_text(copy_quote)}"

        article = item_content.find('a', class_='article_snippet')
        if article:
            post_text = self._get_article(article)

        voting = item_content.find("div", class_="post_media_voting")
        if voting:
            post_text = post_text + self._get_voting(item_content, post_text)

        if not post_text:
            post_text = "."
        post_text = f"{post_text}\n\n{self.author}"

        self.post_text = post_text

        media_urls = self._media_urls_group(photos, gifs, videos)

        return self.post_text, media_urls

    def skip(self, item: BeautifulSoup, db_created: bool) -> bool:
        """Если обнаружена реклама, закреплённый пост или ссылка на источник, то возвращает True, """ \
            """иначе False."""
        if db_created:
            fixed = None
        else:
            fixed = item.parent.find('div', class_='post_fixed')
        ads = item.find('div', class_='wall_marked_as_ads')
        source = item.find('a', class_='Post__copyrightLink')

        if any([fixed, ads, source]):
            return True
        return False

    def _get_text(self, item_content: BeautifulSoup) -> str:
        """Извлечение текста из поста."""
        text_bs4 = item_content.find('div', class_='wall_post_text')

        if text_bs4:
            text_str = str(text_bs4)
            emojis = text_bs4.find_all('img', class_='emoji')
            for emoji_bs4 in emojis:
                emoji = emoji_bs4.get('alt')
                text_str = text_str.replace(str(emoji_bs4), emoji)

            text_str = text_str.replace('<br/>', '\n')
            post_text = BeautifulSoup(text_str, 'html.parser').text
        else:
            post_text = ""
        if "\nПоказать полностью..." in post_text:
            post_text = post_text.replace("\nПоказать полностью...", '')

        return post_text

    def _get_article(self, article: BeautifulSoup) -> str:
        """Получение статьи."""
        article_href = 'https://vk.com' + article.get('href')
        article_title = article.find('div', class_='article_snippet__title').text
        text = article_title + "\n\n" + self.author + "\n\n" + article_href
        return text

    def _get_voting(self, item_content: BeautifulSoup, text: str) -> str:
        """Получения голосования."""
        voting_title = item_content.find('div', class_='media_voting_question').text
        voting_variants = item_content.find_all('div', class_='media_voting_option_text')

        text = text + "\n\nопрос:\n" + voting_title + '\n'
        for i in voting_variants:
            text = f"{text}\n{i.text.split('⋅⋅⋅')[0]}"

        return text

    def _media_urls_group(self, photos: list[BeautifulSoup, ...], gifs: list[BeautifulSoup, ...],
                          videos: list[BeautifulSoup, ...]) -> dict[str or bytes, str, ...]:
        """Создание списка медиа из поста."""
        media = {}

        for photo in photos:
            photo = photo.get('onclick')
            x = photo.split('"x":"')
            y = photo.split('"y":"')
            z = photo.split('"z":"')

            if len(x) > 1:
                photo = x
            if len(y) > 1:
                photo = y
            if len(z) > 1:
                photo = z
            photo_url = photo[1].split('","')[0].replace('\\', '')

            photo = requests.get(photo_url).content
            media[photo] = 'photo'

        for gif in gifs:
            gif_vk_url = "https://vk.com" + gif.get('href')
            gif_page = requests.get(gif_vk_url)
            gif_page = BeautifulSoup(gif_page.text, 'html.parser')
            gif_url = gif_page.find('img').get('src')
            media[gif_url] = 'gif'

        for video in videos:
            video_url = 'https://vk.com' + video.parent.get("href")
            video_url = video_url.replace("clip", "video")  # превратить клипы в видео

            media[video_url] = 'video'

        return media
