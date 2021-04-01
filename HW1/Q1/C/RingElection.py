import socket
import threading
import random
import time

# Lock to use print(). It is used to prevent printing from multiple threads at once.
print_lock = threading.Lock()

# This semaphore waits until all nodes are started and ready to accept connections.
all_start_sema = threading.Semaphore(0)

# This semaphore is used to close all connections and end the program when ring leader is detected.
completed_sema = threading.Semaphore(0)

# lower and upper bound for random id.
LOWER_ID_BOUND = 0
UPPER_ID_BOUND = 1 << 31 - 1

HOST = "127.0.0.1"
PORTS = [5052, 5053, 5054, 5055, 5056]
ENCODING = "ascii"

nodes = []


class Node:
    def __init__(self, host: str, port: int, index: int):
        self.host = host
        self.port = port
        self.index = index
        self.id = random.randint(LOWER_ID_BOUND, UPPER_ID_BOUND)

        # Id that is send to right node. At first, it is the current node id, but it may be updated.
        self.sending_id = self.id

        # Used to listen until left node connect to this node.
        self.receiving_socket: socket.socket = None

        # Left will send messages to this node.
        self.left: socket.socket = None

        # Right is used to send messages from this node to the right node.
        self.right: socket.socket = None

        # Will set this to True when we want to close all sockets.
        self.stopped = False

    def handle_left_node_receive(self):
        try:
            while not self.stopped:
                left_id = int(self.left.recv(1024).decode(ENCODING))
                with print_lock:
                    print(f"node {self.id} recieved {left_id} from its left node.")

                # Main Logic of Election RIng
                if left_id > self.sending_id:
                    self.sending_id = left_id
                elif left_id == self.id:
                    with print_lock:
                        print(f"client-id {self.id} is ring leader")
                        completed_sema.release()  # This line will cause the program to end.
        except:
            self.left.close()

    def handle_right_node_send(self):
        try:
            while not self.stopped:
                self.right.send(str(self.sending_id).encode(ENCODING))
                with print_lock:
                    print(f"{self.id} node sent {self.sending_id} to its right node")
                time.sleep(0.5)
        except:
            self.right.close()

    def start_sending(self):
        self.right = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # (index +1) % 5 means right node. 0->1; 1->2; ...; 4->0.
        self.right.connect((HOST, PORTS[(self.index + 1) % 5]))
        t = threading.Thread(target=self.handle_right_node_send)
        t.start()

    def start_socket(self):
        self.receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiving_socket.bind((self.host, self.port))
        self.receiving_socket.listen(1)  # It will only accept one socket.
        all_start_sema.release()
        conn, addr = self.receiving_socket.accept()
        self.left = conn
        t = threading.Thread(target=self.handle_left_node_receive)
        t.start()

    def close(self):
        self.stopped = True
        self.right.close()
        self.left.close()
        self.receiving_socket.close()

    def __str__(self) -> str:
        return f"{self.host}:{self.port} \t id: {self.id} \t sending_id: {self.sending_id}"


if __name__ == '__main__':
    for i in range(len(PORTS)):
        node = Node(HOST, PORTS[i], i)
        nodes.append(node)
        threading.Thread(target=node.start_socket).start()
    for i in range(len(PORTS)):  # Wait until all nodes are started.
        all_start_sema.acquire(blocking=True)
    with print_lock:
        print("All Started!")
        for i in range(len(nodes)):
            print(f"{i}: {nodes[i]}")
    while True:
        start_cmd = input("Type START to start Election Ring Algorithm: ")
        if start_cmd == "START":
            break
        else:
            print("Invalid Command")

    for i in range(len(nodes)):
        nodes[i].start_sending()

    # Comment following lines to run it indefinitely.
    completed_sema.acquire()
    for node in nodes:
        node.close()
