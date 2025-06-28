import socket

#comando:  python simpleudpclient.py "msg"
class UDP():
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta
        
    def Cliente(self,msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        try:
            s.sendto(bytes(msg, 'utf-8'), (self.ip, self.porta))
            s.close()
        except:
            print("Tempo excedido")

    def Server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, self.porta))
        s.listen(1)
        conn , addr = s.accept()
        with conn:
            print(f"Conectado por {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
        s.close()        
                
if __name__ =='__main__':
    udp = UDP('localhost',6789)
    tcpServer = udp.Server()
                        