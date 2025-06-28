import socket

class TCP():
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def Client(self, msg): 
        self.s.connect((self.ip, self.porta))        
        self.s.sendall(bytes(msg, 'utf-8'))
        data = self.s.recv(1024).decode('utf-8')
        self.s.close()
        print ('FROM SERVER: {s}'.format(s=repr(data)))

    def Server(self):
        self.s.bind((self.ip, self.porta))
        self.s.listen(1)
        while True:
            conn, addr = self.s.accept()
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data.upper())
            conn.close()
