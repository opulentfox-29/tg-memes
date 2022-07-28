import os


if not os.path.isdir("data"):
    os.mkdir("data")
if not os.path.isdir("data/data-base"):
    os.mkdir("data/data-base")
if not os.path.isfile(f"data/links.txt"):
    open("data/links.txt", "w", encoding="utf-8").close()


class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db = []
        
    def check_db(self) -> bool:
        """Если база данных существует, то выводит False, иначе создаёт и выводит True."""
        if not os.path.isfile(f"data/data-base/{self.db_name}"): 
            open("data/data-base/" + self.db_name, "w", encoding="utf-8")
            return True
        return False
            
    def get_db(self) -> list[str, ...]:
        """Достаёт из базы данных все id."""
        self.db = []
        with open('data/data-base/' + self.db_name, "r", encoding="utf-8") as file:
            for line in file:
                self.db.append(line[:-1])
        return self.db
        
    def set_db(self, post_id: str) -> None:
        """Записывает id в базу данных."""
        self.db.insert(0, post_id)
        if len(self.db) > 15:
            self.db.pop()
        with open("data/data-base/" + self.db_name, "w", encoding="utf-8") as new_db:
            for i in self.db:
                new_db.write(i + '\n')
    