from HW1.Q2.Model import Message


class Account:
    def __init__(self, user_id):
        self.user_id = user_id
        self.own_channels: list[str] = []
        self.subscribed_channels: list[str] = []
        self.own_groups: list[str] = []
        self.subscribed_groups: list[str] = []
        self.private_messages: dict[str, list[Message]] = {}

    def __str__(self):
        return self.user_id
