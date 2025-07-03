import socket
import struct
import threading
import time
import uuid
from protos import messages_pb2

# --- Configurações de Rede ---
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007

class Dispositivos:
    """Classe base para todos os dispositivos da cidade inteligente."""
    def __init__(self, tipo):
        self.device_id = f"{tipo.lower().replace(' ', '_')}_{str(uuid.uuid4())[:4]}"
        self.tipo = tipo
        self.ip = '127.0.0.1'
        self.port = 0
        self.estado = False
        self.is_actuator = False

    def __str__(self):
        return f"ID: {self.device_id}, Tipo: {self.tipo}, Endereço: {self.ip}:{self.port}, Estado: {'Ligado' if self.estado else 'Desligado'}"

    def iniciar(self):
        """Inicia os processos de descoberta e o servidor de comandos em threads."""
        print(f"Iniciando dispositivo: {self.device_id}")

        tcp_thread = threading.Thread(target=self.start_tcp_server, daemon=True)
        tcp_thread.start()

        time.sleep(1) # Aguarda a alocação da porta TCP antes de anunciar.

        discovery_thread = threading.Thread(target=self.listen_for_discovery, daemon=True)
        discovery_thread.start()

        print(f"{self.device_id} iniciado. Pressione Ctrl+C para sair.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nDesligando {self.device_id}.")

    def start_tcp_server(self):
        """Inicia o servidor TCP para aguardar conexões do Gateway."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, 0)) # Associa o socket a uma porta aleatória disponível.
        self.port = server.getsockname()[1] # Captura a porta que foi alocada.
        server.listen(5)
        print(f"[{self.device_id}] Servidor TCP escutando em {self.ip}:{self.port}")

        while True:
            conn, addr = server.accept()
            print(f"[{self.device_id}] Gateway conectado via TCP em {addr}")
            self.handle_connection(conn) # Delega o tratamento da conexão.

    def listen_for_discovery(self):
        """Entra no grupo multicast para ser descoberto pelo Gateway."""
        multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multicast_socket.bind(('', MULTICAST_PORT))

        # Configura a subscrição ao grupo multicast.
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"[{self.device_id}] Aguardando descoberta em {MULTICAST_GROUP}:{MULTICAST_PORT}")

        while True:
            data, address = multicast_socket.recvfrom(1024)
            print(f"\n[{self.device_id}] Mensagem de descoberta recebida de {address}")
            self.send_announcement(address)

    def send_announcement(self, gateway_address):
        """Envia uma mensagem de anúncio com seus dados para o Gateway."""
        device_info_payload = messages_pb2.DeviceInfo()
        
        # Converte a string do tipo para o enum correspondente do Protobuf.
        proto_device_type = getattr(messages_pb2, self.tipo.upper(), messages_pb2.UNKNOWN)

        device_info_payload.device_id = self.device_id
        device_info_payload.type = proto_device_type
        device_info_payload.ip_address = self.ip
        device_info_payload.port = self.port
        device_info_payload.is_actuator = self.is_actuator
        
        # Envelopa a mensagem DeviceInfo dentro de uma SmartCityMessage.
        response_message = messages_pb2.SmartCityMessage(devices=device_info_payload)

        gateway_ip = gateway_address[0]
        gateway_data_port = 5008 # Porta UDP de dados do Gateway.
        
        response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Envia a resposta para o IP de origem, mas na porta de dados do Gateway.
        response_socket.sendto(response_message.SerializeToString(), (gateway_ip, gateway_data_port))
        response_socket.close()
        print(f"[{self.device_id}] Anúncio envelopado enviado para o Gateway em {gateway_ip}:{gateway_data_port}.")


class Atuador(Dispositivos):
    """Classe para dispositivos que recebem comandos (atuadores)."""
    def __init__(self, tipo):
        super().__init__(tipo=tipo)
        self.is_actuator = True

    def handle_connection(self, conn):
        """Trata comandos recebidos via TCP (ligar/desligar ou consulta de estado)."""
        try:
            data = conn.recv(1024)
            if data:
                command_msg = messages_pb2.SmartCityMessage()
                command_msg.ParseFromString(data)

                if command_msg.HasField("command"):
                    command = command_msg.command
                    self.estado = command.state
                    msg1 = f"[{self.device_id}] Comando recebido: {'Ligar' if self.estado else 'Desligar'}"
                    msg2 = f"[{self.device_id}] Novo estado: {'Ligado' if self.estado else 'Desligado'}"
                    response_message = f"{msg1}\n{msg2}"

                elif command_msg.HasField("query"):
                    status = "Ligado" if self.estado else "Desligado"
                    response_message = f"[{self.device_id}] Estado atual: {status}"
                else:
                    response_message = f"[{self.device_id}] Comando desconhecido."

                conn.sendall(response_message.encode('utf-8'))
                print(f"[{self.device_id}] Resposta enviada ao cliente.")

        except Exception as e:
            print(f"[{self.device_id}] Erro ao processar comando: {e}")
        finally:
            conn.close()


class Continuos(Dispositivos):
    """Classe para dispositivos que enviam dados continuamente (sensores)."""
    def __init__(self, tipo, data_unit=""):
        super().__init__(tipo=tipo)
        self.is_actuator = False
        self.data_unit = data_unit

    def iniciar(self):
        """Sobrescreve o método 'iniciar' para sensores."""
        print(f"Iniciando sensor: {self.device_id}")

        discovery_thread = threading.Thread(target=self.listen_for_discovery, daemon=True)
        discovery_thread.start()

        gateway_address_for_data = ('127.0.0.1', 5008)

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
            if self.tipo == "TEMPERATURE_SENSOR":
                leitura = round(random.uniform(18.0, 35.0), 2)
            else:
                leitura = round(random.uniform(0.0, 100.0), 2)

            print(f"[{self.device_id}] Nova leitura: {leitura} {self.data_unit}")

            sensor_payload = messages_pb2.SensorData(
                device_id=self.device_id,
                value=leitura,
                unit=self.data_unit
            )
            response_message = messages_pb2.SmartCityMessage(sensor_data=sensor_payload)
            udp_socket.sendto(response_message.SerializeToString(), gateway_address)
            time.sleep(15)


class GerenrenciarCidade:
    """Responsável por criar e iniciar a simulação dos dispositivos."""
    def iniciar_dispositivos_simulados(self, falha=False):
        """Cria e inicia múltiplos dispositivos em threads separadas."""
        if not falha: 
            dispositivos_a_iniciar = [
                Atuador(tipo='LIGHT_POST'),
                Atuador(tipo='TRAFFIC_LIGHT'),
                Atuador(tipo='CAMERA'),
                Continuos(tipo='TEMPERATURE_SENSOR', data_unit="Celsius")
            ]
        else:
            dispositivos_a_iniciar = [
                Atuador(tipo='LIGHT_POST'),
                Atuador(tipo='TRAFFIC_LIGHT'),
                Continuos(tipo='TEMPERATURE_SENSOR', data_unit="Celsius")
            ]

        threads = []
        print("Iniciando simulação da cidade inteligente...")

        for dispositivo in dispositivos_a_iniciar:
            thread = threading.Thread(target=dispositivo.iniciar)
            threads.append(thread)
            thread.start()

        print(f"\n{len(dispositivos_a_iniciar)} dispositivos foram iniciados.")
        print("O gateway agora pode iniciar o processo de descoberta.")
        print("Pressione Ctrl+C neste terminal para parar a simulação.")

        try:
            for t in threads:
                t.join() # Aguarda a finalização das threads (neste caso, nunca ocorre).
        except KeyboardInterrupt:
            print("\nSimulação principal encerrada.")


if __name__ == '__main__':
    print('[1] Cenário Normal [2] Cenário de Falha')
    entrada = input('Digite a opção que você deseja: ')
    
    if entrada == '1':
        try:
            GerenrenciarCidade().iniciar_dispositivos_simulados(falha=False)
        except KeyboardInterrupt:
            print('Encerrado')
    elif entrada == '2':
        GerenrenciarCidade().iniciar_dispositivos_simulados(falha=True)