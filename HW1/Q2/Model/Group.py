from HW1.Q2.Model import Message


class Group:
    def __init__(self, id, owner_id):
        self.id = id
        self.owner_id = owner_id
        self.members: list[str] = []
        self.messages: list[Message] = []
        self.members.append(owner_id)
