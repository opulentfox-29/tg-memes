import os


if not os.path.isdir("data"):
    os.mkdir("data")
if not os.path.isdir("data/data-base"):
    os.mkdir("data/data-base")
if not os.path.isdir("data/temp"):
    os.mkdir("data/temp")
if not os.path.isfile(f"data/links.txt"):
    open("data/links.txt", "w", encoding="utf-8").close()


class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db = []
    
    def check_dir(self) -> None:
        """Очищает временные файлы."""
        temp_files = os.listdir("data/temp")
        for temp_file in temp_files:
            os.remove(f"data/temp/{temp_file}")
        
    def _check_db(self) -> None:
        """Проверяет есть ли база данных, создаёт, если нет."""
        if not os.path.isfile(f"data/data-base/{self.db_name}"): 
            with open("data/data-base/" + self.db_name, "w", encoding="utf-8"):
                pass
            
    def get_db(self) -> list[str, ...]:
        """Достаёт из базы данных все id."""
        self._check_db()
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
    