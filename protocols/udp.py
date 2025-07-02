import socket 
import sys
import os
c = os.path.abspath(os.curdir)
sys.path.insert(0, c)
from protos import messages_pb2

class UDP:
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # O bind deve ser feito na inicialização, não no loop do servidor
        self.sock.bind((self.ip, self.porta))
        print(f"Servidor UDP escutando em {self.ip}:{self.porta}")

    def Client(self, msg_bytes):
        # A função cliente deve receber bytes, não uma string, 
        # pois o Protobuf já serializa para bytes.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            try:
                s.sendto(msg_bytes, (self.ip, self.porta))
            except socket.timeout:
                print("Tempo excedido ao enviar mensagem UDP.")
            except Exception as e:
                print(f"Erro ao enviar mensagem UDP: {e}")

    def Server(self, handler_function):
        """
        Inicia o servidor e chama a 'handler_function' para cada pacote recebido.
        Isso desacopla a lógica de rede da lógica de aplicação.
        
        Args:
            handler_function (function): Uma função que aceita (data, addr) como argumentos.
        """
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data:
                    # Delega o processamento do pacote para a função handler
                    handler_function(data, addr)
            except Exception as e:
                print(f"Erro no servidor UDP: {e}")


def handle_udp_packet(self, data, addr):
    """
    Processa os pacotes UDP recebidos, que podem ser anúncios ou dados de sensores.
    Esta função seria passada para o `udp_server.Server()`.
    """
    message = messages_pb2.SmartCityMessage()
    try:
        message.ParseFromString(data)
    except Exception as e:
        print(f"[Gateway UDP] Erro ao decodificar Protobuf de {addr}: {e}")
        return

    # --- CORREÇÃO PRINCIPAL ---
    # Verifica o campo 'devices' e acessa o atributo 'devices'
    if message.HasField("devices"):
        # Acessa o atributo correto: message.devices
        device_info = message.devices
        
        print(f"[Gateway UDP] Anúncio de dispositivo recebido de {addr}: ID={device_info.device_id}")
        
        # Adiciona ao dicionário que pertence à classe Gateway/Multicast
        # Assumindo que self.discovered_devices existe na sua classe principal
        if hasattr(self, 'discovered_devices'):
            self.discovered_devices[device_info.device_id] = (device_info, addr)
            print(f"[Gateway UDP] Dispositivo '{device_info.device_id}' adicionado à lista.")
            # print('Lista atual:', self.discovered_devices) # Descomente para debug pesado
        else:
            print("[Gateway UDP] ERRO: O objeto não tem um atributo 'discovered_devices' para armazenar o dispositivo.")

    elif message.HasField("sensor_data"):
        sensor_data = message.sensor_data
        print(f"[Gateway UDP] Dados de sensor recebidos de {sensor_data.device_id}: {sensor_data.value} {sensor_data.unit}")
        # Aqui você pode, por exemplo, salvar os dados em um banco de dados
        # ou encaminhá-los para uma interface de usuário.

    else:
        print(f"[Gateway UDP] Pacote UDP de {addr} recebido, mas com tipo de payload desconhecido.")
              
if __name__ =='__main__':
    udp = UDP('localhost',6789)
    tcpServer = udp.Server()
                        