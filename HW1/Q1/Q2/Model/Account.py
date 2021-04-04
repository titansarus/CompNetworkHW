from HW1.Q1.Q2.Model import Channel, Group
import socket
import threading


class Account:
    def __init__(self, user_id, s: socket):
        self.user_id = user_id
        self.own_channels: list[Channel] = []
        self.subscribed_channels: list[Channel] = []
        self.own_groups: list[Group] = []
        self.subscribed_groups: list[Group] = []
        self.sock = s

    def __str__(self):
        return self.user_id


