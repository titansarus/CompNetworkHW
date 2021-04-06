import socket

HOST = "127.0.0.1"
PORT = 5052
ENCODING = "ascii"

if __name__ == '__main__':
    with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as s:
        s.bind((HOST , PORT))
        s.listen()

        conn,addr = s.accept()
        with conn:
            print(f"[CONNECTED] {addr}")
            while True:
                data1 = conn.recv(1024).decode(ENCODING)
                if not data1:
                    break
                print(f"[RECEIVED] {data1}")
                data2 = conn.recv(1024).decode(ENCODING)
                if not data2:
                    break
                print(f"[RECEIVED] {data2}")
                try:
                    result = int(data1) + int(data2)
                    conn.send(str(result).encode(ENCODING))
                except:
                    conn.send("Invalid Arguments".encode(ENCODING))

