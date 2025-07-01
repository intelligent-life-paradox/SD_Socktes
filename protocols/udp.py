import socket
from protos import messages_pb2
import sys
import os
c = os.path.abspath(os.curdir)
sys.path.insert(0, c)
from protos import messages_pb2

#from interface import obter_dados_sensores

#comando:  python simpleudpclient.py "msg"
class UDP():
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta
        
    def Client(self,msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        try:
            s.sendto(bytes(msg, 'utf-8'), (self.ip, self.porta))
            s.close()
        except:
            print("Tempo excedido")

    def Server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        s.bind((self.ip, self.porta))
        print(f"Servidor UDP escutando em {self.ip}:{self.porta}")

        while True:
            try:
                data, addr = s.recvfrom(1024) 
                
                print(f"Recebido {len(data)} bytes de {addr}")
                print(f"  -> Mensagem: {messages_pb2.SmartCityMessage.FromString(data)}") # Exemplo de decodificação
                #obter_dados_sensores(messages_pb2.SmartCityMessage.FromString(data).value)
                s.sendto(b"Resposta do servidor UDP!", addr)

            except KeyboardInterrupt:
                print("\nServidor UDP encerrado.")
                break
            except Exception as e:
                print(f"Ocorreu um erro: {e}")
        
        s.close()       
    def sendApplication(self):
        return              
if __name__ =='__main__':
    udp = UDP('localhost',6789)
    tcpServer = udp.Server()
                        