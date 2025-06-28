import socket

class TCP():
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta
      
    def Client(self, msg): 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.porta))        
        s.sendall(bytes(msg, 'utf-8'))
        data = s.recv(1024).decode('utf-8')
        s.close()
        print ('FROM SERVER: {s}'.format(s=repr(data)))

    def Server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, self.porta))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data.upper())
            conn.close()
