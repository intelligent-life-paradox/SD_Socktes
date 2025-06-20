import socket

PORT = 6789
HOST = 'localhost'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
msg = input()
s.sendall(bytes(msg, 'utf-8'))
data = s.recv(1024).decode('utf-8')
s.close()
print ('FROM SERVER: {s}'.format(s=repr(data)))