import socket

IP ='127.0.0.1'
PORT = 65342
message = b"Hello, World!"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((IP, PORT))
    s.listen(1)
    conn , addr = s.accept()
    with conn:
        print(f"Conectado por {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)