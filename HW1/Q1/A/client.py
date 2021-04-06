import socket

HOST = "127.0.0.1"
PORT = 5052
ENCODING = "ascii"

if __name__ == '__main__':
    with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        num1 = input("Input First Number: ")
        num2 = input("Input Second Number: ")
        s.send(num1.encode(ENCODING))
        s.send(num2.encode(ENCODING))
        print(s.recv(1024).decode(ENCODING))