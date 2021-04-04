class Account:
    def __init__(self, user_id):
        self.user_id = user_id
        self.own_channels: list[str] = []
        self.subscribed_channels: list[str] = []
        self.own_groups: list[str] = []
        self.subscribed_groups: list[str] = []

    def __str__(self):
        return self.user_id


