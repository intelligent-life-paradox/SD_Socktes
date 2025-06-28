import messages_pb2
import socket
import struct 
''' string tipo = 1; 
  string ip = 2;
  int32 porta = 3;
  string msg = 4;'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def sendMessage(tipo, ip, porta, msg, estado, protocolo):
    comunication = messages_pb2.Comunicacao()
    comunication.tipo = tipo
    comunication.ip = ip
    comunication.porta = porta
    comunication.msg = msg
    data = struct.pack('H',comunication)

    if protocolo == 'TCP':
      print(data)
      print(comunication.SerializeToString())
      print(comunication.ParseFromString(comunication.SerializeToString()))
    elif protocolo =='UDP':
      ...
    elif protocolo =='MULTI':
      ...        

#if __name__=='__main__':
sendMessage('localhost', '3',12345, 'msg',True,'TCP')