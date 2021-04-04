from HW1.Q1.Q2.Model import Account, Message


class Group:
    def __init__(self, id, owner_id):
        self.id = id
        self.owner_id = owner_id
        self.members: list[Account] = []
        self.messages: list[Message] = []
