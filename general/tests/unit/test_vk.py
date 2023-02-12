from django.test import TestCase

from general.utils.vkontakte import Vk


class VKTestCase(TestCase):
    vk = Vk(1024)
    def test_parse_main_page(self):
        items = self.vk.parse_main_page('https://vk.com/reddit')
        self.assertIsInstance(items, tuple, 'Should be tuple')
        self.assertEqual(len(items), 10, 'Should be 10 items')
        with self.assertRaises(AssertionError):
            self.vk.parse_main_page('https://vk.com/Qdm.s/<&?JNS_20-=1')

