# dispositivos.py (Versão Refatorada com Lógica de Rede)
import os
import sys

c = os.path.abspath(os.curdir)
sys.path.insert(0, c)

import socket
import struct
import threading
import time
import uuid
from protos import messages_pb2

# Importa as classes de mensagem do arquivo compilado


# --- Configurações de Rede (Comuns a todos) ---
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007

class Dispositivos:
    """Classe base para todos os dispositivos da cidade inteligente."""
    
    def __init__(self, tipo):
        self.device_id = f"{tipo.lower().replace(' ', '_')}_{str(uuid.uuid4())[:4]}"
        self.tipo = tipo
        self.ip = '127.0.0.1'  # IP do próprio dispositivo para o servidor TCP
        self.port = 0          # Porta TCP será alocada dinamicamente
        self.estado = False    # Estado padrão (ex: desligado)
        self.is_actuator = False # Por padrão, um dispositivo é um sensor

    def __str__(self):
        return f"ID: {self.device_id}, Tipo: {self.tipo}, Endereço: {self.ip}:{self.port}, Estado: {'Ligado' if self.estado else 'Desligado'}"

    def iniciar(self):
        """Inicia os processos de descoberta e o servidor de comandos em threads."""
        print(f"Iniciando dispositivo: {self.device_id}")
        
        # Inicia o servidor TCP em uma thread para escutar por comandos
        tcp_thread = threading.Thread(target=self.start_tcp_server, daemon=True)
        tcp_thread.start()
        
        # Aguarda um instante para garantir que a porta TCP foi alocada
        time.sleep(1)

        # Inicia o listener de descoberta multicast em outra thread
        discovery_thread = threading.Thread(target=self.listen_for_discovery, daemon=True)
        discovery_thread.start()

        # Mantém o programa principal rodando
        print(f"{self.device_id} iniciado. Pressione Ctrl+C para sair.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nDesligando {self.device_id}.")

    def start_tcp_server(self):
        """Lógica do servidor TCP que fica aguardando conexões do Gateway."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, 0))
        self.port = server.getsockname()[1] # Captura a porta alocada
        server.listen(5)
        print(f"[{self.device_id}] Servidor TCP escutando em {self.ip}:{self.port}")

        while True:
            conn, addr = server.accept()
            print(f"[{self.device_id}] Gateway conectado via TCP em {addr}")
            # Delega o tratamento da conexão para um método que pode ser sobrescrito
            self.handle_connection(conn)

    def listen_for_discovery(self):
        """Lógica do listener UDP Multicast para ser descoberto pelo Gateway."""
        multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multicast_socket.bind(('', MULTICAST_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"[{self.device_id}] Aguardando descoberta em {MULTICAST_GROUP}:{MULTICAST_PORT}")

        while True:
            data, address = multicast_socket.recvfrom(1024)
            print(f"\n[{self.device_id}] Mensagem de descoberta recebida de {address}")
            self.send_announcement(address)

    def send_announcement(self, gateway_address):
        """Envia a mensagem de anúncio (Protocol Buffers) para o Gateway."""
        response_message = messages_pb2.SmartCityMessage()
        
        proto_device_type = getattr(messages_pb2, self.tipo.upper(), messages_pb2.UNKNOWN)

        response_message.Devices.device_id = self.device_id
        response_message.Devices.type = proto_device_type
        response_message.Devices.ip_address = self.ip
        response_message.Devices.port = self.port
        response_message.Devices.is_actuator = self.is_actuator

        response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        response_socket.sendto(response_message.SerializeToString(), gateway_address)
        response_socket.close()
        print(f"[{self.device_id}] Anúncio enviado para o Gateway.")
        
    def handle_connection(self, conn):
        """Método placeholder para lidar com conexões TCP. Será sobrescrito."""
        print(f"[{self.device_id}] Conexão recebida, mas nenhum handler definido.")
        conn.close()


class Atuador(Dispositivos):
    """Classe para dispositivos que recebem comandos, como postes e semáforos."""
    
    def __init__(self, tipo):
        super().__init__(tipo=tipo)
        self.is_actuator = True # Define que este tipo de dispositivo é um atuador

    def handle_connection(self, conn):
        """Sobrescreve o método da classe pai para tratar comandos específicos de atuadores."""
        try:
            data = conn.recv(1024)
            if data:
                command_msg = messages_pb2.SmartCityMessage()
                command_msg.ParseFromString(data)

                if command_msg.HasField("command"):
                    command = command_msg.command
                    self.estado = command.state # Atualiza o estado
                    print(f"[{self.device_id}] Comando recebido: {'Ligar' if self.estado else 'Desligar'}")
                    print(f"[{self.device_id}] Novo estado: {'Ligado' if self.estado else 'Desligado'}")
        except Exception as e:
            print(f"[{self.device_id}] Erro ao processar comando: {e}")
        finally:
            conn.close()

# Adicione esta classe no final do arquivo dispositivos.py

class Continuos(Dispositivos):
    """Classe para dispositivos que enviam dados continuamente, como sensores."""
    
    def __init__(self, tipo, data_unit=""):
        super().__init__(tipo=tipo)
        self.is_actuator = False # Sensores não são atuadores
        self.data_unit = data_unit # Ex: "Celsius", "µg/m³"

    def iniciar(self):
        """Sobrescreve o método iniciar para sensores."""
        print(f"Iniciando sensor: {self.device_id}")
        
        # Sensores também precisam ser descobertos
        discovery_thread = threading.Thread(target=self.listen_for_discovery, daemon=True)
        discovery_thread.start()

        # A principal diferença: em vez de um servidor TCP,
        # ele inicia uma rotina para enviar dados periodicamente.
        # Vamos simular o Gateway estando em um endereço conhecido para enviar os dados.
        # Na prática, o dispositivo descobriria o endereço do gateway da mesma forma que o gateway descobre o dispositivo.
        # Por simplicidade, vamos usar um endereço fixo.
        gateway_address_for_data = ('127.0.0.1', 5008) # Porta de dados do Gateway (exemplo)
        
        data_thread = threading.Thread(target=self.start_sending_data, args=(gateway_address_for_data,), daemon=True)
        data_thread.start()

        print(f"{self.device_id} iniciado. Pressione Ctrl+C para sair.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nDesligando {self.device_id}.")

    def start_sending_data(self, gateway_address):
        """Envia dados simulados para o gateway a cada 15 segundos."""
        import random

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"[{self.device_id}] Enviando dados para o Gateway em {gateway_address}")
        
        while True:
            # Simula uma leitura de sensor
            if self.tipo == "TEMPERATURE_SENSOR":
                # Gera uma temperatura aleatória entre 18.0 e 35.0
                leitura = round(random.uniform(18.0, 35.0), 2)
            else:
                # Gera um valor genérico para outros sensores
                leitura = round(random.uniform(0.0, 100.0), 2)

            print(f"[{self.device_id}] Nova leitura: {leitura} {self.data_unit}")

            # Monta a mensagem Protobuf
            sensor_payload = messages_pb2.SensorData(
                device_id=self.device_id,
                value=leitura,
                unit=self.data_unit
            )
            response_message = messages_pb2.SmartCityMessage(sensor_data=sensor_payload)

            # Envia via UDP [cite: 21]
            udp_socket.sendto(response_message.SerializeToString(), gateway_address)
            
            # Aguarda 15 segundos para a próxima leitura [cite: 24]
            time.sleep(15)