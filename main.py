import os
import vkontakte
from telegram import TG
import database
import logger as log
import settings


def main():

    with open("data/links.txt", "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file]
    if not urls:
        log.error("Введите ссылки в файле 'data/links.txt'")

    for url in urls:
        log.log("="*20)
        log.log(f"{url=}")

        db_name = url.split("/")[3]

        vk = vkontakte.Vk()
        db = database.DataBase(db_name)
        db_created = db.check_db()

        items = vk.parse_main_page(url)

        new_items = False

        for item in items:

            db.check_dir()

            if vk.skip(item, db_created):
                continue  # скип закрепа, рекламы, источника

            ids_in_db = db.get_db()
            post_id = vk.get_post_id(item)

            if post_id in ids_in_db:
                continue  # скип постов, которые уже в базе
            new_items = True

            text, media_urls = vk.item_parse(item)

            tg = TG(settings.TOKEN, settings.chat_id, text, vk.link_post, media_urls)

            tg.send_post()

            db.set_db(post_id)
        if not new_items:
            log.log("no new items")


if __name__ == "__main__":
    if settings.dont_use_proxy:
        os.environ['no_proxy'] = '*'

    if settings.cycle:
        while True:
            main()
    else:
        main()
    input('Press enter to continue...')
