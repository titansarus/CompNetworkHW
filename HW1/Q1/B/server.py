import socket
import threading

HOST = "127.0.0.1"
PORT = 5052
ENCODING = "ascii"

clients = []
numbers = []
numbers_lock = threading.Lock()
client_sema = threading.Semaphore(0)
result_sema = threading.Semaphore(0)


def handle_client(conn: socket.socket, addr):
    print(f"[CONNECTED] {addr}")
    with conn:
        while True:
            data = conn.recv(1024).decode(ENCODING)
            if not data:
                break
            print(f"[RECEIVED] {data}")
            try:
                data = int(data)
                with numbers_lock:
                    numbers.append(data)
            except:
                conn.send("Invalid Argument".encode(ENCODING))
            with numbers_lock:
                if len(numbers) == 2:
                    result_sema.release()
            client_sema.acquire(blocking=True)
            print("Wake Up!")


def broadcast(msg: str):
    for client in clients:
        client.send(msg.encode(ENCODING))


def handle_sum():
    while True:
        result_sema.acquire()
        result = numbers[0] + numbers[1]
        numbers.clear()
        broadcast(str(result))
        client_sema.release()
        print("Next Cycle")
        client_sema.release()
        print("Next Cycle")


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        sum_thread = threading.Thread(target=handle_sum)
        sum_thread.start()
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            clients.append(conn)
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
