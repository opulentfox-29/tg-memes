import requests
from bs4 import BeautifulSoup

from . import logger as log
from . import exceptions
from .extractors import extractor_url

headers = {
    'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
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

        self.link_post = 'https://vk.com' + item.find('a', class_='PostHeaderSubtitle__link').get('href')
        item_content = item.find("div", class_="wall_text")

        photos = item_content.find_all('div', class_='MediaGrid__interactive')
        photo = item_content.find('a', {'aria-label': 'фотография'})
        if photo:
            photos += photo
        wall_id = None
        if photos:
            wall_id = item.find('a', class_='PostHeaderSubtitle__link').get('href').split('/')[1]

        ui_gallery = item_content.find_all('img', class_='PhotoPrimaryAttachment__imageElement')
        ui_gallery = [i.get('src') for i in ui_gallery]

        gifs = item_content.find_all('a', {'class': 'page_doc_photo_href'})
        videos_collection = item_content.find_all('a', class_="MediaGrid__interactive")
        one_video = item_content.find('div', class_="page_post_video_play_inline")
        if one_video:
            videos_collection += [one_video]

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

        self.media_bytes_dict = self._create_media_bytes_dict(wall_id, gifs, videos_collection, ui_gallery)

        return self.post_text, self.media_bytes_dict

    def skip(self, item: BeautifulSoup, db_created: bool) -> bool:
        """Если обнаружена реклама, закреплённый пост или ссылка на источник, то возвращает True, """ \
            """иначе False."""
        if db_created:
            fixed = None
        else:
            fixed = item.parent.find('div', class_='post_fixed')
        ads = item.find('div', class_='wall_marked_as_ads')
        ads2 = item.find('span', class_='PostHeaderSubtitle__item')
        ads3 = item.find('a', class_='PostHeaderSubtitle__item')
        source = item.find('a', class_='Post__copyrightLink')

        if any([fixed, ads, ads2, ads3, source]):
            return True
        return False

    def _get_text(self, item_content: any) -> str:
        """Извлечение текста из поста."""
        text_bs4 = item_content.find('div', class_='wall_post_text')

        if text_bs4:
            text_more = text_bs4.find('button', class_='PostTextMore')
            text_str = str(text_bs4)
            if text_more:
                text_more = str(text_more)
                text_str = text_str.replace(text_more, '')
            emojis = text_bs4.find_all('img', class_='emoji')
            for emoji_bs4 in emojis:
                emoji = emoji_bs4.get('alt')
                text_str = text_str.replace(str(emoji_bs4), emoji)

            hrefs = text_bs4.find_all('a')
            for href in hrefs:
                text = href.text
                if text.startswith('https://'):
                    continue
                link = href.get('href')
                text_str = text_str.replace(str(href), f"{text}({link})")

            text_str = text_str.replace('<br/>', '\n')
            post_text = BeautifulSoup(text_str, 'html.parser').text
        else:
            post_text = ""

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
                                 videos_collection: list[BeautifulSoup, ...],
                                 ui_gallery: list[str, ...]) -> dict[bytes, dict[str, str, str, dict[str, str]], ...]:
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

        for link in ui_gallery:
            photo = requests.get(link).content
            media[photo] = {'type': 'photo'}

        for gif in gifs:
            gif_vk_url = "https://vk.com" + gif.get('href')
            gif_page = requests.get(gif_vk_url).text
            gif_url = gif_page.split('"docUrl":"')[1].split('",')[0].replace('\\', '')
            gif_bin = requests.get(gif_url).content
            media[gif_bin] = {'type': 'gif'}

        for video in videos_collection:
            if video.get('aria-label') == 'фотография':
                continue
            if 'page_post_video_play_inline' in video.get('class'):
                video = video.parent
                video_restriction = video.find('div', class_='VideoRestriction__title')
                if video_restriction:
                    log.warning(f"[get video] - {video_restriction.text}")
                    self.post_text = f"[get video] - {video_restriction.text}.\n{self.post_text}\n{self.link_post}"
                    continue
            video_url = 'https://vk.com' + video.get("href")
            video_url = video_url.replace("clip", "video")  # превратить клипы в видео
            try:
                extract_url, duration, width, height = extractor_url(video_url)
            except Exception as ex_err:
                log.error(f"extractor_url - {ex_err}")
                continue
            video_bytes = self._download_video(extract_url)
            if video_bytes:
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
            return video_bytes

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
