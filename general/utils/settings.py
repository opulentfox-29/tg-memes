from . import database


db = database.DataBase()
db.cur.execute("""SELECT "general_settings"."token", "general_settings"."chat_id", "general_settings"."chunk_size", "general_settings"."cycle", "general_settings"."dont_use_proxy" FROM "general_settings" ORDER BY "general_settings"."id" ASC LIMIT 1""")
settings = db.cur.fetchone()
token, chat_id, chunk_size, cycle, dont_use_proxy = settings
