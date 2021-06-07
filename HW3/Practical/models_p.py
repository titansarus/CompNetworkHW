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
        self.auto_advertise = False

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

    # delete range ip and send withdrawn message to ASs
    def withdrawn_ip(self, range_ip):
        self.owned_ips.remove(range_ip)
        path = [self.as_number, range_ip]
        for my_link in self.connected_AS:
            AS.send_message(my_link, MESSAGE_TYPE.WITHDRAW, path, range_ip)

    # propagate withdrawn message
    def withdrawn_path(self, path):
        if {PATH_CONST: path[PATH_CONST], RANGE_IP_CONST: path[RANGE_IP_CONST]} in self.path_ips:
            self.path_ips.remove({PATH_CONST: path[PATH_CONST], RANGE_IP_CONST: path[RANGE_IP_CONST]})
        self.advertise_or_withdraw(path, False)
        # Propagation is handled in receive message

    # advertise this range ip fraudulently
    def hijack(self, hijack_range_ip):
        path = [self.as_number, hijack_range_ip]
        for my_link in self.connected_AS:
            AS.send_message(my_link, MESSAGE_TYPE.ADVERTISE, path, hijack_range_ip)

    # advertise your ips
    def advertise_self(self):
        for ip in self.owned_ips:
            path = [self.as_number, ip]
            for my_link in self.connected_AS:
                AS.send_message(my_link, MESSAGE_TYPE.ADVERTISE, path, ip)

    def advertise_all(self):
        # advertise my range_ips to all neighbours
        self.advertise_self()

        # advertise other paths
        for adv_path in self.path_ips:
            self.advertise_or_withdraw(adv_path, True)

    def advertise_or_withdraw_to_specific_link(self, path, is_advertise, link):
        # Don't Propagate If I am in the path or I have gotten the path recently from the same link (to prevent loops)
        if self.as_number in path[PATH_CONST] or int(path[PATH_CONST][0]) == link.peer_as_number:
            return

        send_path = [self.as_number] + path[PATH_CONST]
        path_owner_role = self.get_role(int(path[PATH_CONST][0]))

        neighbour_role = self.get_role((int(link.peer_as_number)))

        # Send all paths to my customers
        if neighbour_role == ROLES.COSTUMER:
            AS.send_message(link, MESSAGE_TYPE.ADVERTISE if is_advertise else MESSAGE_TYPE.WITHDRAW, send_path,
                            path[RANGE_IP_CONST])
            return
            # Send customer's paths to Peers or Providers but don't send other paths
        elif neighbour_role == ROLES.PEER or neighbour_role == ROLES.PROVIDER:
            # Actually the elif above could be replaced by else, it is stated in this way to be completely explicit.

            if path_owner_role == ROLES.COSTUMER:
                AS.send_message(link, MESSAGE_TYPE.ADVERTISE if is_advertise else MESSAGE_TYPE.WITHDRAW,
                                send_path,
                                path[RANGE_IP_CONST])
            return

    # Utility function to send advertise or withdraw message to neighbours, by following the rules of advertisement.
    def advertise_or_withdraw(self, path, is_advertise):
        # If my AS number is in path, don't propagate (to prevent loops)
        if self.as_number in path[PATH_CONST]:
            return
        for my_link in self.connected_AS:
            self.advertise_or_withdraw_to_specific_link(path, is_advertise, my_link)

    # Check whether previously known paths to the ip_range really belong to the AS claiming that it owns  range_ip.
    def check_hijack(self, ip_range, claiming_as):
        for path in self.path_ips:
            path_ip = path[RANGE_IP_CONST]
            if subnet_of(ip_range, path_ip):
                if int(path[PATH_CONST][-2]) != int(claiming_as):
                    return True
        return False

    # use for receiving a message from a link.
    def receive_message(self, message, sender_as_number):
        changed = False  # changes is a flag to check whether anything changed
        received_path = {PATH_CONST: message[PATH_CONST], RANGE_IP_CONST: message[RANGE_IP_CONST]}
        if message[MESSAGE_TYPE_CONST] == MESSAGE_TYPE.ADVERTISE:
            # If message is advertise, check if it is hijacked or not, if not, add it to paths.
            if self.check_hijack(received_path[RANGE_IP_CONST], received_path[PATH_CONST][-2]):
                self.print(f'{received_path[RANGE_IP_CONST]} hijacked.')
                return

            if self.path_ips.count(received_path) == 0:
                # if my AS number is in the path, don't add it into my paths to prevent loops.
                if not self.as_number in received_path[PATH_CONST]:
                    self.path_ips.append(received_path)
                    changed = True

        if message[MESSAGE_TYPE_CONST] == MESSAGE_TYPE.WITHDRAW:
            # Withdraw path
            if self.path_ips.count(received_path):
                self.path_ips.remove(received_path)
                changed = True
                self.withdrawn_path(received_path)

        # If anything changed and auto_advertise is true, advertise all you know.
        if changed and self.auto_advertise:
            self.advertise_or_withdraw(received_path, True if message[
                                                                  MESSAGE_TYPE_CONST] == MESSAGE_TYPE.ADVERTISE else False)
        return

    # print reachable path to this range ip (use bgp algorithm)
    # print ' None + range_ip 'if it doesn't exist
    def get_route(self, range_ip):
        # Search in AS IPs
        for ip in self.owned_ips:
            if subnet_of(range_ip, ip):
                self.print(f'[{self.as_number}] {range_ip}')
                return

        # Find valid paths that go through other ASes
        valid_paths = []
        for path in self.path_ips:
            if subnet_of(range_ip, path[RANGE_IP_CONST]):
                valid_paths.append(path)

        # Classify path into three categories (customer, peer, and provider)
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

        # Get a sorted list first by prioritizing customer>peer>provider and then by length of path
        if len(customer_paths):
            sorted_list = sorted(customer_paths, key=lambda x: (len(x[PATH_CONST]), x[PATH_CONST][-2::-1]))
        elif len(peer_paths):
            sorted_list = sorted(peer_paths, key=lambda x: (len(x[PATH_CONST]), x[PATH_CONST][-2::-1]))
        elif len(provider_paths):
            sorted_list = sorted(provider_paths, key=lambda x: (len(x[PATH_CONST]), x[PATH_CONST][-2::-1]))
        else:
            self.print(f'None {range_ip}')
            return

        # Print path
        out_str = f'['
        for i in range(len(sorted_list[0][PATH_CONST]) - 2, -1, -1):
            out_str += f'{sorted_list[0][PATH_CONST][i]}, '
        out_str += f'{self.as_number}] {range_ip}'
        self.print(out_str)
        return

    def withdraw_path_to_as(self, as_number):
        path_to_withdraw = []
        for path in self.path_ips:
            if int(path[PATH_CONST][0]) == as_number:
                path_to_withdraw.append(path)
        for path in path_to_withdraw:
            self.withdrawn_path(path)

    # Handle deletion of a link
    def delete_link(self, as_number):
        delete_link = None
        for link in self.connected_AS:
            if int(link.peer_as_number) == int(as_number):
                delete_link = link
                break
        if delete_link:
            first_as: AS = delete_link.link.first_as
            second_as: AS = delete_link.link.second_as
            first_as.withdraw_path_to_as(second_as.as_number)
            second_as.withdraw_path_to_as(first_as.as_number)
            self.connected_AS.remove(delete_link)
            first_as.delete_link(second_as.as_number)
            second_as.delete_link(first_as.as_number)

    # Handle creation of a link
    # this link has already been added to your  self.connected_AS
    def create_link(self, as_number):
        # Add the link to the other AS, If it is not added yet.
        as_link = self.get_link(int(as_number))

        # Advertise all my paths to the recently linked AS.
        for ip in self.owned_ips:
            path = [self.as_number, ip]
            AS.send_message(as_link, MESSAGE_TYPE.ADVERTISE, path, ip)
        for path in self.path_ips:
            self.advertise_or_withdraw_to_specific_link(path, True, as_link)

    @staticmethod
    def send_message(link, is_advertise, path, range_ip):
        link.send_message({
            MESSAGE_TYPE_CONST: is_advertise,
            PATH_CONST: path,
            RANGE_IP_CONST: range_ip
        })

    def get_role(self, as_number):
        return self.get_link(as_number).role

    def get_link(self, as_number):
        return next(filter(lambda link_as: link_as.peer_as_number == as_number, self.connected_AS))

    def print(self, *message):
        print("AS " + str(self.as_number) + ":", *message)


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
