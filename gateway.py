''' O Gateway deve receber e enviar via tcp'''
#from protocols import tcpcliente, tcpserver
from protos import messages_pb2 as comunication
from protocols import tcp, udp, multicast
import threading
import socket

class Gateway():
    def __init__(self):
       # instanciando os servidores de recepção
       self.tcpServer = tcp.TCP('localhost',6789) 
       self.udpServer = udp.UDP('localhost',6789)
       
       self.multicastServer = multicast.Mulicast()

    def start(self):
        print("Gateway iniciando todos os serviços...")
        
        tcp_thread = threading.Thread(target=self.tcpServer.Server())
        
        udp_thread = threading.Thread(target=self.udpServer.Server())
        
        multicast_thread = threading.Thread(target=self.multicastServer.Server())

        tcp_thread.start()
        udp_thread.start()
        multicast_thread.start()

    print("Gateway rodando. Pressione Ctrl+C para sair.")
    def listarDispistivos():
        ...
    def ComandoDispostivos():
        ...
                  
    def accpetConections(self,serverSocket):
        while True:
            clientSocket , clienteAdress = serverSocket.accept()
            print(f'Nova conexão de {clienteAdress}')
            clientThread = threading.Thread(target = self.receiveClients, args = (clientSocket, clienteAdress))
            clientThread.start()

    def receiveClients(clientSocket, clienteAdress):
        try:
            while True:
                msg = clientSocket.recv(1024).decode('utf-8')
                if not msg:
                    break
                print(f'Recebido de {clienteAdress}:{msg}')
                clientSocket.sendall(f"Servidor recebeu: {msg}".encode('utf-8'))
        except Exception as e:
            clientSocket.close()
            print(f"Conexão com {clienteAdress} fechada")

if __name__ == "__main__":
    Gateway().start()
