from bs4 import BeautifulSoup

from django.test import TestCase

from general.utils.vkontakte import Vk


class VKTestCase(TestCase):
    def setUp(self):
        self.vk = Vk(1024)
        with open('general/tests/fixtures/reddit.html', 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            self.items = tuple(reversed(soup.find_all('div', class_='post')))
            self.vk.author = soup.find('h1', class_='page_name').text

    def test_item_parse_photo(self):
        data = self.vk.item_parse(self.items[2])
        post_text, media_bytes_dict = data
        media_bytes_dict = str(media_bytes_dict)
        with open('general/tests/fixtures/item_parse_photo_text.txt', 'r', encoding='utf-8') as f:
            current_post_text = f.read()
        with open('general/tests/fixtures/item_parse_photo_dict.txt', 'r', encoding='utf-8') as f:
            current_media_bytes_dict = f.read()
        self.assertEqual(post_text, current_post_text, 'Text photo error')
        self.assertEqual(media_bytes_dict, current_media_bytes_dict, 'Media photo error')

    def test_item_parse_article(self):
        data = self.vk.item_parse(self.items[0])
        post_text, media_bytes_dict = data
        media_bytes_dict = str(media_bytes_dict)
        with open('general/tests/fixtures/item_parse_article_text.txt', 'r', encoding='utf-8') as f:
            current_post_text = f.read()
        with open('general/tests/fixtures/item_parse_article_dict.txt', 'r', encoding='utf-8') as f:
            current_media_bytes_dict = f.read()
        self.assertEqual(post_text, current_post_text, 'Text article error')
        self.assertEqual(media_bytes_dict, current_media_bytes_dict, 'Media article error')

    def test_item_parse_video(self):
        data = self.vk.item_parse(self.items[1])
        post_text, media_bytes_dict = data
        media_bytes_dict = str(media_bytes_dict)
        with open('general/tests/fixtures/item_parse_video_text.txt', 'r', encoding='utf-8') as f:
            current_post_text = f.read()
        with open('general/tests/fixtures/item_parse_video_dict.txt', 'r', encoding='utf-8') as f:
            current_media_bytes_dict = f.read()
        self.assertEqual(post_text, current_post_text, 'Text video error')
        self.assertEqual(media_bytes_dict, current_media_bytes_dict, 'Media video error')

    def test_get_post_id(self):
        ids = '\n'.join([self.vk.get_post_id(item) for item in self.items])
        with open('general/tests/fixtures/get_post_id_ids.txt', 'r', encoding='utf-8') as f:
            current_ids = f.read()
        self.assertEqual(ids, current_ids, 'Ids error')
