import os
from . import vkontakte
from .telegram import TG
from . import database
from . import logger as log
from . import settings


def bot():
    urls = database.DataBase('').get_urls()

    for url in urls:
        log.log("="*20)
        log.log(f"{url=}")

        db_name = url.split("/")[3]

        vk = vkontakte.Vk(settings.chunk_size)
        db = database.DataBase(db_name)
        db_created = db.check_db()

        items = vk.parse_main_page(url)

        new_items = False

        for item in items:

            if vk.skip(item, db_created):
                continue  # скип закрепа, рекламы, источника

            ids_in_db = db.get_db()
            post_id = vk.get_post_id(item)

            if post_id in ids_in_db:
                continue  # скип постов, которые уже в базе
            new_items = True

            vk.item_parse(item)

            tg = TG(settings.token, settings.chat_id, vk)

            tg.send_post()

            db.set_db(post_id)
        if not new_items:
            log.log("no new items")


def main():
    if settings.dont_use_proxy:
        os.environ['no_proxy'] = '*'

    if settings.cycle:
        while True:
            bot()
    else:
        bot()
    input('Press enter to continue...')


if __name__ == "__main__":
    main()
