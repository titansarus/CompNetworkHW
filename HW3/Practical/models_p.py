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

PATH_CONST = "path"
RANGE_IP_CONST = "range_ip"
MESSAGE_TYPE_CONST = "message_type"

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
        send_path = [self.as_number] + path[PATH_CONST]
        path_owner_role = self.get_role(int(path[PATH_CONST][0]))
        for my_link in self.connected_AS:
            if (int(path[PATH_CONST][0]) == my_link.peer_as_number):
                continue
            if self.get_role(int(my_link.peer_as_number)) == ROLES.PEER and path_owner_role == ROLES.PEER:
                continue
            if self.get_role(int(my_link.peer_as_number)) == ROLES.PROVIDER and path_owner_role == ROLES.PROVIDER:
                continue
            AS.send_message(my_link, MESSAGE_TYPE.WITHDRAW, send_path, path[RANGE_IP_CONST])

        # HINT function
        # propagate withdrawn message

    pass

    def hijack(self, hijack_range_ip):
        path = [self.as_number, hijack_range_ip]
        for my_link in self.connected_AS:
            AS.send_message(my_link, MESSAGE_TYPE.ADVERTISE, path, hijack_range_ip)
        # advertise this range ip fraudly

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
            send_path = [self.as_number] + adv_path[PATH_CONST]
            path_owner_role = self.get_role(int(adv_path[PATH_CONST][0]))
            for my_link in self.connected_AS:
                if (int(adv_path[PATH_CONST][0]) == my_link.peer_as_number):
                    continue
                if self.get_role(int(my_link.peer_as_number)) == ROLES.PEER and path_owner_role == ROLES.PEER:
                    continue
                if self.get_role(int(my_link.peer_as_number)) == ROLES.PROVIDER and path_owner_role == ROLES.PROVIDER:
                    continue
                AS.send_message(my_link, MESSAGE_TYPE.ADVERTISE, send_path, adv_path[RANGE_IP_CONST])
        # advertise all paths you know (include yourself ips)
        pass

    def check_hijack(self, ip_range, claiming_as):
        for path in self.path_ips:
            path_ip = path[RANGE_IP_CONST]
            if subnet_of(ip_range, path_ip):
                if int(path[PATH_CONST][-2]) != int(claiming_as):
                    return True
        return False

    def receive_message(self, message, sender_as_number):
        changed = False
        if message[MESSAGE_TYPE_CONST] == MESSAGE_TYPE.ADVERTISE:
            my_path = {PATH_CONST: message[PATH_CONST], RANGE_IP_CONST: message[RANGE_IP_CONST]}
            if self.check_hijack(my_path[RANGE_IP_CONST], my_path[PATH_CONST][-2]):
                print(f'AS {self.as_number}: {my_path[RANGE_IP_CONST]} hijacked.')
                return

            if self.path_ips.count(my_path) == 0:
                self.path_ips.append(my_path)
                changed = True

        if message[MESSAGE_TYPE_CONST] == MESSAGE_TYPE.WITHDRAW:
            remove_path = {PATH_CONST: message[PATH_CONST], RANGE_IP_CONST: message[RANGE_IP_CONST]}
            if self.path_ips.count(remove_path):
                self.path_ips.remove(remove_path)
                changed = True
                self.withdrawn_path(remove_path)

        if changed and self.auto_advertise:
            self.advertise_all()
        # use for receiving a message from a link.
        #
        return

    def get_route(self, range_ip):
        for ip in self.owned_ips:
            if subnet_of(range_ip, ip):
                print(f'AS {self.as_number}: [{self.as_number}] {range_ip}')
                return

        valid_paths = []
        for path in self.path_ips:
            if subnet_of(range_ip, path[RANGE_IP_CONST]):
                valid_paths.append(path)

        customer_paths = []
        peer_paths = []
        provider_paths = []
        for path in valid_paths:
            role = self.get_role(path[PATH_CONST][0])
            if role == ROLES.COSTUMER:
                customer_paths.append(path)
            elif role == ROLES.PEER:
                peer_paths.append(path)
            elif role == ROLES.PROVIDER:
                provider_paths.append(path)
            else:
                raise NotImplementedError
        sorted_list = []
        if len(customer_paths):
            sorted_list = sorted(customer_paths, key=lambda x: len(x[PATH_CONST]))
        elif len(peer_paths):
            sorted_list = sorted(peer_paths, key=lambda x: len(x[PATH_CONST]))
        elif len(provider_paths):
            sorted_list = sorted(provider_paths, key=lambda x: len(x[PATH_CONST]))
        else:
            print(f'AS {self.as_number}: None {range_ip}')
            return
        out_str = f'AS {self.as_number}: ['
        for i in range(len(sorted_list[0]) - 1, -1, -1):
            out_str += f'{sorted_list[0][PATH_CONST][i]}, '
        out_str += f'{self.as_number}] {range_ip}'
        print(out_str)
        return

        # print reachable path to this range ip (use bgp algorithm)
        # print ' None + range_ip 'if it doesn't exist
        pass

    def delete_link(self, as_number):
        # TODO TEST
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
            MESSAGE_TYPE_CONST: is_advertise,
            PATH_CONST: path,
            RANGE_IP_CONST: range_ip
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
