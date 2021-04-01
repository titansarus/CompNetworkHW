import socket
import threading
import random
import time

print_lock = threading.Lock()
all_start_sema = threading.Semaphore(0)

LOW_ID_BOUND = 0
HIGH_ID_BOUND = 1 << 31 - 1

HOST = "127.0.0.1"
PORTS = [5052, 5053, 5054, 5055, 5056]
ENCODING = "ascii"
nodes = []


class Node:
    def __init__(self, host: str, port: int, index: int):
        self.host = host
        self.port = port
        self.index = index
        self.id = random.randint(LOW_ID_BOUND, HIGH_ID_BOUND)
        self.sending_id = self.id
        self.receiving_socket: socket.socket = None
        self.left: socket.socket = None
        self.right: socket.socket = None
        self.threads = []
        self.stopped = False

    def handle_left_node_receive(self):
        try:
            while not self.stopped:
                left_id = int(self.left.recv(1024).decode(ENCODING))
                if left_id > self.sending_id:
                    self.sending_id = left_id
                elif left_id == self.id:
                    with print_lock:
                        print(f"client-id {self.id} is ring leader")
        except Exception as e:
            with print_lock:
                print(e)
            self.left.close()

    def handle_right_node_send(self):
        try:
            while not self.stopped:
                self.right.send(str(self.sending_id).encode(ENCODING))
                time.sleep(0.5)
        except Exception as e:
            with print_lock:
                print(e)
            self.right.close()

    def start_sending(self):
        self.right = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.right.connect((HOST, PORTS[(self.index + 1) % 5]))
        t = threading.Thread(target=self.handle_right_node_send)
        t.start()

    def start_socket(self):
        self.receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiving_socket.bind((self.host, self.port))
        self.receiving_socket.listen(1)
        all_start_sema.release()
        conn, addr = self.receiving_socket.accept()
        self.left = conn
        t = threading.Thread(target=self.handle_left_node_receive)
        t.start()

    def __str__(self) -> str:
        return f"{self.host}:{self.port} \t id: {self.id} \t sending_id: {self.sending_id}"


if __name__ == '__main__':
    for i in range(len(PORTS)):
        node = Node(HOST, PORTS[i], i)
        nodes.append(node)
        threading.Thread(target=node.start_socket).start()
    for i in range(len(PORTS)):
        all_start_sema.acquire(blocking=True)
    with print_lock:
        print("All Started!")
        for i in range(len(nodes)):
            print(nodes[i])
    while True:
        start_cmd = input("Input START to start Election Ring Algorithm: ")
        if start_cmd == "START":
            break

    for i in range(len(nodes)):
        nodes[i].start_sending()
