import socket
import threading

HOST = "127.0.0.1"
PORT = 5052
ENCODING = "ascii"

clients = []
numbers = []

# This lock is used to access 'numbers' list.
numbers_lock = threading.Lock()

# This semaphore is used for clients. So after a client put one number in 'numbers', it waits until the other number is
# also added to the array and their sum calculated. When the sum is calculated we will release this semaphore two times
# to let two client handlers work again.
client_sema = threading.Semaphore(0)

# This semaphore is used in handle_sum. It will cause it to wait until one of clients check that there are two numbers
# in 'numbers'. When there are two numbers in list, they will wake the thread that is handling handle_sum.
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
                with numbers_lock:  # Lock for synchronization.
                    numbers.append(data)
            except:
                conn.send("Invalid Argument".encode(ENCODING))
            with numbers_lock:
                if len(numbers) == 2:  # release semaphore to let another thread calculate their sum.
                    result_sema.release()

            # Wait until two numbers are put in 'numbers' and their sum is calculated. After their sum is calculated,
            # and the result is broadcasted, this thread is unblocked.
            client_sema.acquire(blocking=True)


def broadcast(msg: str):
    for client in clients:
        client.send(msg.encode(ENCODING))


def handle_sum():
    while True:
        # Wait until there are two numbers in 'numbers'. One of the client handlers will wake this thread.
        result_sema.acquire()
        result = numbers[0] + numbers[1]
        numbers.clear()
        broadcast(str(result))
        client_sema.release()
        client_sema.release()


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
