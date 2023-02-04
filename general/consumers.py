import json
import base64

from channels.consumer import SyncConsumer

from .models import Settings, Links, Posts
from .utils import vkontakte, telegram


class WebConsumer(SyncConsumer):

    def websocket_connect(self, event):
        print('connect')
        self.send({"type": "websocket.accept"})

    def websocket_receive(self, event):
        print('receive')
        receive_data = json.loads(event['text'])

        if receive_data['status'] == 'start':
            settings = Settings.objects.first()
            if settings.cycle:
                while True:
                    self._bot(settings)
            else:
                self._bot(settings)

        if receive_data['status'] == 'settings':
            settings_data = receive_data['settings']
            settings = Settings.objects.first()
            settings.token = settings_data['token']
            settings.chat_id = settings_data['chat_id']
            settings.chunk_size = settings_data['chunk_size']
            settings.cycle = settings_data['cycle']
            settings.dont_use_proxy = settings_data['dont_use_proxy']
            settings.save()
            [i.delete() for i in Links.objects.all()]
            links = settings_data['links'].split('\n')
            [Links.objects.create(link=i) for i in links]

    def websocket_disconnect(self, event):
        print('disconnect')

    def _bot(self, settings):
        urls = list(Links.objects.all())

        for url in urls:
            url = url.link

            db_name = url.split("/")[3]

            vk = vkontakte.Vk(settings.chunk_size)

            db_created = False if Posts.objects.filter(group=db_name) else True

            items = vk.parse_main_page(url)

            for item in items:

                if vk.skip(item, db_created):
                    continue  # скип закрепа, рекламы, источника

                ids_in_db = [i.id_post for i in Posts.objects.filter(group=db_name)]
                post_id = vk.get_post_id(item)

                if post_id in ids_in_db:
                    continue  # скип постов, которые уже в базе

                vk.item_parse(item)

                tg = telegram.TG(settings.token, settings.chat_id, vk)

                medias = []
                for i in vk.media_bytes_dict:
                    media_type = vk.media_bytes_dict[i]['type']
                    medias.append({'type': media_type, 'base64': str(base64.b64encode(i))})

                data = {
                    'text': vk.post_text,
                    'medias': medias,
                }
                data_json = json.dumps(data)

                self.send({
                    "type": "websocket.send",
                    "text": str(data_json)
                })

                tg.send_post()

                ids_in_db.insert(0, post_id)

                ids_in_db = ids_in_db[0:15]
                [i.delete() for i in Posts.objects.filter(group=db_name)]
                for i in ids_in_db:
                    Posts.objects.create(id_post=i, group=db_name)
