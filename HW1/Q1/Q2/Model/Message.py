import datetime


class Message:
    def __init__(self, author, message, timestamp):
        self.author = author
        self.message: str = message
        self.timestamp: datetime.datetime = timestamp

    def __str__(self):
        return f"{self.author}@{self.timestamp}: {self.message}"
