import socket
import threading
import time
from protos import messages_pb2
from protocols import tcp, udp, multicast

class Gateway:
    """
    Componente central do sistema. Gerencia a descoberta de dispositivos,
    roteia comandos de clientes e recebe dados de sensores.
    """
    def __init__(self):
        self.tcpServer = tcp.TCPServer('localhost', 5009, handler_function=self.handle_client_command)
        self.udpServer = udp.UDP('0.0.0.0', 5008) # Escuta em todas as interfaces.
        self.multicastServer = multicast.Mulicast()
        self.discovered_devices = {} # Dicionário para armazenar dispositivos online.

    def start(self):
        """Inicia todos os serviços do gateway em threads separadas."""
        print("Gateway iniciando todos os serviços...")

        tcp_thread = threading.Thread(target=self.tcpServer.Server, daemon=True)
        # Passa a função de tratamento de pacotes para o servidor UDP.
        udp_thread = threading.Thread(target=self.udpServer.Server, args=(self.handle_udp_packet,), daemon=True)
        discovery_thread = threading.Thread(target=self.multicastServer.Server, daemon=True)

        tcp_thread.start()
        udp_thread.start()
        discovery_thread.start()
        
        print("Gateway está online. Pressione Ctrl+C para sair.")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nEncerrando o Gateway...")

    def handle_udp_packet(self, data, addr):
        """Processa pacotes UDP recebidos (anúncios ou dados de sensores)."""
        try:
            message = messages_pb2.SmartCityMessage()
            message.ParseFromString(data)
            
            if message.HasField("devices"):
                device_info = message.devices
                self.discovered_devices[device_info.device_id] = (device_info, addr)
                print(f"[Gateway] Dispositivo '{device_info.device_id}' adicionado/atualizado.")

            elif message.HasField("sensor_data"):
                sensor_data = message.sensor_data
                print(f"[Gateway UDP] Dados de sensor de {sensor_data.device_id}: {sensor_data.value} {sensor_data.unit}")
        
        except Exception as e:
            print(f"[Gateway UDP] Pacote de {addr} não pôde ser decodificado: {e}")

    def handle_client_command(self, client_socket, client_address):
        """Processa comandos TCP recebidos do cliente."""
        print(f"[Gateway] Lidando com o comando de {client_address}")
        try:
            command_str = client_socket.recv(1024).decode('utf-8').strip()
            parts = command_str.split(';')
            main_command = parts[0]
            
            resposta_para_cliente = "ERRO: Comando não processado."
            
            if main_command == 'LIGAR_DISPOSITIVO' and len(parts) == 3:
                tipo_dispositivo = int(parts[1])
                ligar = self.falsetrue(parts[2])
                device_info_tuple = self.encontraDispositivo(tipo_dispositivo)
                if device_info_tuple:
                    resposta_do_dispositivo = self.send_command_to_device(device_info_tuple[0], ligar=ligar)
                    resposta_para_cliente = resposta_do_dispositivo
                else:
                    resposta_para_cliente = f"ERRO: Nenhum dispositivo do tipo {tipo_dispositivo} encontrado."
            
            elif main_command == 'CONSULTAR_DISPOSITIVO' and len(parts) == 3:
                tipo_dispositivo = int(parts[1])
                consultar = self.falsetrue(parts[2])
                device_info_tuple = self.encontraDispositivo(tipo_dispositivo)
                if device_info_tuple:
                    resposta_do_dispositivo = self.send_command_to_device(device_info_tuple[0], consultar=consultar)
                    resposta_para_cliente = resposta_do_dispositivo
                else:
                    resposta_para_cliente = f"ERRO: Nenhum dispositivo do tipo {tipo_dispositivo} encontrado."

            elif main_command == "LISTAR_DISPOSITIVOS":
                resposta_para_cliente = self.listarDispositivos()
            
            else:
                resposta_para_cliente = "ERRO: Comando desconhecido ou formato inválido."

            if resposta_para_cliente is None:
                resposta_para_cliente = f"ERRO: Falha na comunicação com o dispositivo."

            client_socket.sendall(resposta_para_cliente.encode('utf-8'))
        
        except Exception as e:
            print(f"[Gateway] Erro ao processar cliente: {e}")
        finally:
            client_socket.close()

    def send_command_to_device(self, device_info, ligar=True, consultar=None):
        """Conecta-se a um atuador, envia um comando e retorna sua resposta."""
        try:
            device_ip = device_info.ip_address
            device_port = device_info.port
            print(f"Gateway: Conectando ao dispositivo {device_info.device_id} em {device_ip}:{device_port}...")
            
            if consultar is not None:
                command_payload = messages_pb2.Query(status=consultar)
                message_to_send = messages_pb2.SmartCityMessage(query=command_payload)
            else:
                command_payload = messages_pb2.Command(state=ligar)
                message_to_send = messages_pb2.SmartCityMessage(command=command_payload)

            serialized_message = message_to_send.SerializeToString()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((device_ip, device_port))
                s.sendall(serialized_message)
                response_bytes = s.recv(1024)
                return response_bytes.decode('utf-8') if response_bytes else None
        
        except socket.timeout:
            print(f"ERRO: Timeout ao esperar resposta do dispositivo {device_info.device_id}.")
            return None
        except Exception as e:
            print(f"ERRO ao se comunicar com o dispositivo {device_info.device_id}: {e}")
            return None
            
    def listarDispositivos(self):
        """Retorna uma string formatada com os IDs dos dispositivos online."""
        if not self.discovered_devices:
            return "--- Dispositivos Online ---\nNenhum dispositivo encontrado."

        linhas_resposta = "--- Dispositivos Online ---\n"
        for device_info_obj, addr in self.discovered_devices.values():
           linhas_resposta += f'{device_info_obj.device_id}\n'
        return linhas_resposta
    
    def encontraDispositivo(self, tipo_int):
        """Busca o primeiro dispositivo de um tipo específico na lista de descobertos."""
        for device_info_obj, addr in self.discovered_devices.values():
            if device_info_obj.type == tipo_int:
                print(f"Dispositivo do tipo '{messages_pb2.DeviceType.Name(tipo_int)}' encontrado: {device_info_obj.device_id}")
                return (device_info_obj, addr)
        
        print(f"Nenhum dispositivo do tipo '{messages_pb2.DeviceType.Name(tipo_int)}' foi encontrado.")
        return None
        
    def falsetrue(self, valor):
        """Converte uma string 'true'/'false' para um booleano."""
        return valor.lower() == 'true'

if __name__ == "__main__":
    gw = Gateway()
    gw.start()