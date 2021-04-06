import datetime


class Message:
    def __init__(self, author, message):
        self.author = author
        self.message: str = message
        self.timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def __str__(self):
        return f"{self.author}@{self.timestamp}: {self.message}"
