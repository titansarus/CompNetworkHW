from enum import Enum
import ipaddress
from typing import List


class ROLES(Enum):
    COSTUMER = -1
    PEER = 0
    PROVIDER = 1


class MESSAGE_TYPE(Enum):
    ADVERTISE = 1
    WITHDRAW = -1


class LinkedAS:
    def __init__(self, peer_as_number, our_as_number, link, role):
        self.our_as_number = our_as_number
        self.peer_as_number = peer_as_number
        self.link = link
        self.role = role

    def send_message(self, message):
        self.link.send_message(message, self.our_as_number)


def subnet_of(r1, r2):  # is r1 subnet of r2
    return ipaddress.ip_network(r1).subnet_of(ipaddress.ip_network(r2))


class AS:
    def __init__(self, as_number, connected_AS: List[LinkedAS] = None, owned_ips=None):
        # owned_ips is a list from all range ips owned by this AS , ['5.0.0.0/8','12.2.0.0/16' , ... ]
        self.as_number = as_number
        self.connected_AS = connected_AS if connected_AS else list()
        self.owned_ips = owned_ips if owned_ips else list()
        self.path_ips = []
        pass

    def add_link(self, linked_AS: LinkedAS):
        self.connected_AS.append(linked_AS)

    def command_handler(self, command):
        command: str
        if command == "advertise all":
            self.advertise_all()
        elif command == "advertise self":
            self.advertise_self()
        elif command.startswith("get route"):
            self.get_route(command.split()[2])
        elif command.startswith("hijack"):
            self.hijack(command.split()[1])
        elif command.startswith("withdrawn"):
            self.withdrawn_ip(command.split()[1])
        elif command.startswith("link"):
            if command.split()[1] == "delete":
                self.delete_link(command.split()[2])
            else:
                self.create_link(command.split()[2])
        elif command == "auto advertise on":
            self.auto_advertise = True
        # handle commands
        # advertise all
        # advertise self
        # get route [prefix] # example: get route "12.4.0.0/16"
        # hijack [prefix]
        # withdrawn [prefix] #
        # link [delete/create] [AS_number]
        # when auto advertise is on you must advertise paths immediately after receiving it
        pass

    def withdrawn_ip(self, range_ip):
        self.owned_ips.remove(range_ip)
        path = [self.as_number, range_ip]
        for my_link in self.connected_AS:
            AS.send_message(my_link, MESSAGE_TYPE.WITHDRAW, path, range_ip)
        # delete range ip and send withdrawn message to ASs
        pass

    def withdrawn_path(self, path):
        send_path = [self.as_number] + path["path"]
        path_owner_role = self.get_role(int(path["path"][0]))
        for my_link in self.connected_AS:
            if (int(path["path"][0]) == my_link.peer_as_number):
                continue
            if self.get_role(int(my_link.peer_as_number)) == ROLES.PEER and path_owner_role == ROLES.PEER:
                continue
            if self.get_role(int(my_link.peer_as_number)) == ROLES.PROVIDER and path_owner_role == ROLES.PROVIDER:
                continue
            AS.send_message(my_link, MESSAGE_TYPE.WITHDRAW, send_path, path["range_ip"])

        # HINT function
        # propagate withdrawn message

    pass

    def hijack(self, hijack_range_ip):
        path = [self.as_number, hijack_range_ip]
        for my_link in self.connected_AS:
            AS.send_message(my_link, MESSAGE_TYPE.ADVERTISE, path, hijack_range_ip)
        # advertise this range ip fraudly
        pass

    def advertise_self(self):
        for ip in self.owned_ips:
            path = [self.as_number, ip]
            for my_link in self.connected_AS:
                AS.send_message(my_link, MESSAGE_TYPE.ADVERTISE, path, ip)

        # your code
        # advertise your ips
        pass

    def advertise_all(self):
        self.advertise_self()
        for adv_path in self.path_ips:
            send_path = [self.as_number] + adv_path["path"]
            path_owner_role = self.get_role(int(adv_path["path"][0]))
            for my_link in self.connected_AS:
                if (int(adv_path["path"][0]) == my_link.peer_as_number):
                    continue
                if self.get_role(int(my_link.peer_as_number)) == ROLES.PEER and path_owner_role == ROLES.PEER:
                    continue
                if self.get_role(int(my_link.peer_as_number)) == ROLES.PROVIDER and path_owner_role == ROLES.PROVIDER:
                    continue
                AS.send_message(my_link, MESSAGE_TYPE.ADVERTISE, send_path, adv_path["range_ip"])
        # advertise all paths you know (include yourself ips)
        pass

    def check_hijack(self , ip_range, claiming_as):
        for path in self.path_ips:
            path_ip = path["range_ip"]
            if subnet_of(ip_range , path_ip):
                if (int(path["path"][-2])!=int(claiming_as)):
                    return True
        return False
    
    def receive_message(self, message, sender_as_number):
        if message["is_advertise"] == MESSAGE_TYPE.ADVERTISE:
            my_path = {"path": message["path"], "range_ip": message["range_ip"]}


            # TODO CHECK FOR HIJACK
            if self.path_ips.count(my_path)==0:
                self.path_ips.append(my_path)
                self.advertise_all()

        if message["is_advertise"] == MESSAGE_TYPE.WITHDRAW:
            remove_path = {"path": message["path"], "range_ip": message["range_ip"]}
            if self.path_ips.count(remove_path):
                self.path_ips.remove(remove_path)
                self.withdrawn_path(remove_path)

        # use for receiving a message from a link.
        #
        return

    def get_route(self, range_ip):
        # print reachable path to this range ip (use bgp algorithm)
        # print ' None + range_ip 'if it doesn't exist
        pass

    def delete_link(self, as_number):
        #TODO TEST
        delete_link = None
        for link in self.connected_AS:
            if link.peer_as_number == as_number:
                delete_link = link
                break
        if delete_link:
            self.connected_AS.remove(delete_link)
            delete_link.link.first_as.delete_link(self.as_number)
            delete_link.link.second_as.delete_link(self.as_number)
        # handle deletion of a link
        pass

    def create_link(self, as_number):
        # handle creation of a link
        # this link has already been added to your  self.connected_AS
        pass

    @staticmethod
    def send_message(link, is_advertise, path, range_ip):
        link.send_message({
            "is_advertise": is_advertise,
            "path": path,
            "range_ip": range_ip
        })

    def get_role(self, as_number):
        return self.get_link(as_number).role
        pass

    def get_link(self, as_number):
        return next(filter(lambda link_as: link_as.peer_as_number == as_number, self.connected_AS))
        pass

    def print(self, *message):
        print("AS " + str(self.as_number) + ":", *message)
        pass


# This class handles communication between 2 ASes.
class Link:
    def __init__(self, first_as: AS, second_as: AS):
        self.first_as = first_as
        self.second_as = second_as

    def send_message(self, message, sender_as_id):
        if sender_as_id == self.first_as.as_number:
            self.second_as.receive_message(message, sender_as_id)
        elif sender_as_id == self.second_as.as_number:
            self.first_as.receive_message(message, sender_as_id)
        else:
            raise ValueError("Invalid target-AS.")
