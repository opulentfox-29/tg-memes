dont_use_proxy = True  # не использовать прокси
cycle = False  # должен ли бот работать циклично.
chunk_size = 1024

try:
    with open("data/session", "r", encoding="utf-8") as session:
        TOKEN, chat_id = session.read().split('\n')
except Exception:
    TOKEN = input("Enter your tg token: ")
    chat_id = input("Enter your chat id: ")
    with open("data/session", "w", encoding="utf-8") as session:
        session.write(f"{TOKEN}\n{chat_id}")
