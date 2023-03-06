import os
import sqlite3
import psycopg2


class DataBase:
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.db = []
        if os.environ.get('db') == 'postgresql':
            self.conn = psycopg2.connect(
                host=os.environ.get('db_host', '127.0.0.1'),
                user=os.environ.get('db_user', 'postgres'),
                password=os.environ.get('db_password', 'postgres'),
                database=os.environ.get('db_name', 'postgres')
            )
        else:
            self.conn = sqlite3.connect('db.sqlite3')
        self.cur = self.conn.cursor()

    def get_urls(self):
        """Получает список ссылок."""
        self.cur.execute("""SELECT "link" FROM "general_links" """)
        urls = self.cur.fetchall()
        urls = [i[0] for i in urls]
        return urls
        
    def check_db(self) -> bool:
        """Если база данных существует, то выводит False, иначе создаёт и выводит True."""
        self.cur.execute(f"""SELECT "general_posts"."id_post" FROM "general_posts" WHERE "general_posts"."group" = \'{self.db_name}\'""")
        posts = self.cur.fetchall()
        if posts:
            return False
        return True

    def get_db(self) -> list[str, ...]:
        """Достаёт из базы данных все id."""
        self.db = []
        self.cur.execute(f"""SELECT "general_posts"."id_post" FROM "general_posts" WHERE "general_posts"."group" = \'{self.db_name}\'""")
        posts = self.cur.fetchall()
        posts = [i[0] for i in posts]
        self.db = posts
        return self.db
        
    def set_db(self, post_id: str) -> None:
        """Записывает id в базу данных."""
        self.db.insert(0, post_id)
        self.db = self.db[0:15]

        self.cur.execute(f"""DELETE FROM "general_posts" WHERE "general_posts"."group" = \'{self.db_name}\'""")
        self.conn.commit()

        for i in self.db:
            self.cur.execute(f"""INSERT INTO "general_posts" ("id_post", "group") VALUES (\'{i}\', \'{self.db_name}\')""")
            self.conn.commit()
