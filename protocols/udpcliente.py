import socket
import sys

#comando:  python simpleudpclient.py "msg"

msg = "msgggggg"
HOST = "127.0.0.1"
PORT = 6789
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(1)

try:
    s.sendto(bytes(msg, 'utf-8'), (HOST, PORT))
    s.close()
except:
    print("Tempo excedido")
