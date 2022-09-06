import os
import requests
from bs4 import BeautifulSoup

import logger as log
import exceptions
from extractors import extractor_url, extractor_info

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}


class Vk:
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.author = None
        self.link_post = None
        self.post_text = None
        self.err_text = ''
        self.media_bytes_dict = {}

    def parse_main_page(self, url: str) -> tuple[BeautifulSoup, ...]:
        """Возвращает кортеж постов."""
        soup = self._get_page(url)
        items = tuple(reversed(soup.find_all('div', class_='post')))
        assert len(items) == 10, f"{len(items)=}"
        self.author = soup.find('h1', class_='page_name').text
        return items

    def _get_page(self, url: str) -> BeautifulSoup:
        """Возвращает soup страницы."""
        try:
            request = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError as err:
            log.error(f"[ERROR] невозможно открыть ссылку {err}")
            raise requests.exceptions.ConnectionError(err)
        soup = BeautifulSoup(request.text, 'html.parser')
        return soup

    def get_post_id(self, item: BeautifulSoup) -> str:
        """Возвращает id поста."""
        post_id = item.get('id')
        return post_id

    def item_parse(self, item: BeautifulSoup) -> tuple[str, list[str, ...]] or None:
        """Возвращает данные из поста (текст поста, ссылки на медиа)."""

        self.link_post = 'https://vk.com' + item.find('a', class_='post_link').get('href')
        item_content = item.find("div", class_="wall_text")

        photos = item_content.find_all('a', {'aria-label': 'фотография'})
        wall_id = None
        if photos:
            wall_id = item.find('a', class_='post_link').get('href').split('/')[1]

        gifs = item_content.find_all('a', {'class': 'page_doc_photo_href'})
        videos = item_content.find_all('div', class_="page_post_video_play_inline")

        post_text = self._get_text(item_content)

        copy_quote = item_content.find('div', class_='copy_quote')  # Репост
        if copy_quote:
            author_copy = copy_quote.find('a', class_='copy_author').text
            post_text = f"{post_text}\nРЕПОСТ: {author_copy}\n\n{self._get_text(copy_quote)}"

        article = item_content.find('a', class_='article_snippet')  # Статья
        if article:
            post_text = self._get_article(article)

        voting = item_content.find("div", class_="post_media_voting")  # Голосование
        if voting:
            post_text = post_text + self._get_voting(item_content, post_text)

        if not post_text:
            post_text = "."
        post_text = f"{post_text}\n\n{self.author}"

        self.post_text = post_text

        self.media_bytes_dict = self._create_media_bytes_dict(wall_id, gifs, videos)

        return self.post_text, self.media_bytes_dict

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

    def _get_text(self, item_content: any) -> str:
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

    def _get_article(self, article: any) -> str:
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

    def _create_media_bytes_dict(self, wall_id: str, gifs: list[BeautifulSoup, ...],
                                 videos: list[BeautifulSoup, ...]) -> dict[bytes,
                                                                           dict[str, str, str, dict[str, str]], ...]:
        """Создание списка медиа из поста."""
        media = {}

        if wall_id:
            headers = {
                'x-requested-with': 'XMLHttpRequest'
            }

            data = {
                'al': '1',
                'list': wall_id
            }

            photos = requests.post('https://vk.com/al_photos.php?act=show', headers=headers, data=data)
            photos = photos.json()['payload'][1][3]

            for photo in photos:
                photo_url = photo.get('w_src') or photo.get('z_src') or photo.get('y_src') or photo.get('x_src')
                photo = requests.get(photo_url).content
                media[photo] = {'type': 'photo'}

        for gif in gifs:
            gif_vk_url = "https://vk.com" + gif.get('href')
            gif_page = requests.get(gif_vk_url)
            gif_page = BeautifulSoup(gif_page.text, 'html.parser')
            gif_url = gif_page.find('img').get('src')
            gif_bin = requests.get(gif_url).content
            media[gif_bin] = {'type': 'gif'}

        for video in videos:
            video_url = 'https://vk.com' + video.parent.get("href")
            video_url = video_url.replace("clip", "video")  # превратить клипы в видео
            extract_url, duration = extractor_url(video_url)

            download_data = self._download_video(extract_url)
            if download_data:
                video_bytes, width, height = download_data
                media[video_bytes] = {'type': 'video', 'data': {'duration': duration, 'width': width, 'height': height}}

        return media

    def _download_video(self, extract_url: str) -> bytes or None:
        try:
            chunk_size = self.chunk_size
            with requests.get(extract_url, headers=headers, stream=True) as vid_req:
                vid_len_bytes = int(vid_req.headers['Content-Length'])
                vid_len = round(vid_len_bytes / 1024 / 1024, 1)
                if vid_len_bytes >= 50 * 1024 * 1024:
                    raise exceptions.TooLargeVideo(vid_len)
                download_bytes = 0
                chunks = []
                for chunk in vid_req.iter_content(chunk_size=chunk_size):
                    download_bytes += chunk_size
                    log.download_video(download_bytes, vid_len)
                    chunks.append(chunk)
                video_bytes = b''.join(chunks)
                log.download_video(download_bytes, vid_len, finished=True)
            with open('data/temp_vid.mp4', 'wb') as f:
                f.write(video_bytes)
            width, height = extractor_info()
            return video_bytes, width, height

        except exceptions.TooLargeVideo as ex:
            log.warning(ex.text)
            self.err_text = f"{self.err_text}{ex.text}\n"
        except KeyError as ex:
            if "www.youtube.com" in extract_url:
                self.post_text = f"{self.post_text}\n{extract_url}"
                log.warning(f"[download video] Видео с youtube не скачиваются.")
            else:
                self.err_text = f"{self.err_text}KeyError: {ex}\n"
                log.error(extract_url)
                log.error(f"[download video] KeyError: {ex}")
        except KeyboardInterrupt:
            self.err_text = f"{self.err_text}SKIP DOWNLOAD VIDEO\n"
            log.warning(f"\n[download video] SKIP DOWNLOAD VIDEO")
        except Exception as ex:
            self.err_text = f"{self.err_text}{ex}\n"
            log.error(f"FAILED DOWNLOAD VIDEO {ex}")
        finally:
            if os.path.isfile(f"data/temp_vid.mp4"):
                os.remove("data/temp_vid.mp4")
