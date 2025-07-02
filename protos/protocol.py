import messages_pb2
import socket
import struct 
''' string tipo = 1; 
  string ip = 2;
  int32 porta = 3;
  string msg = 4;'''

class ProtoBuf():
    def __init__(self):
       self.comunication = messages_pb2.Comunicacao()
       
    def marshalling(self,tipo, ip, porta, msg, estado, protocolo):
        
        self.comunication.tipo = tipo
        self.comunication.ip = ip
        self.comunication.porta = porta
        self.comunication.msg = msg

        buffer = self.comunication.SerializeToString()
        return buffer
    
    def unmarshalling(self, data):
        return messages_pb2.Comunicacao.FromString(data)     

if __name__=='__main__':
   serializable = ProtoBuf().marshalling('localhost', '3',12345,'msg',True,'TCP')
   print(ProtoBuf().unmarshalling(serializable))