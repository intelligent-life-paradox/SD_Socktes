# gateway.py (Versão Limpa e Corrigida)

from protos import messages_pb2 
from protocols import tcp, udp, multicast
import threading
import time
import socket

class Gateway():
    def __init__(self):
       # Suas inicializações de servidor
       self.tcpServer = tcp.TCPServer('localhost', 5009, handler_function=self.handle_client_command)
       self.udpServer = udp.UDP('0.0.0.0', 5008)
       self.multicastServer = multicast.Mulicast()
       
       self.discovered_devices = {}

    def start(self):
        """Inicia todos os serviços do gateway e os mantém rodando."""
        print("Gateway iniciando todos os serviços...")
        
        # Thread para o servidor TCP que lida com os comandos do cliente
        tcp_thread = threading.Thread(target=self.tcpServer.Server, daemon=True)
        
        # Thread para o servidor UDP, que recebe anúncios de TODOS os dispositivos
        # Passamos a função 'handle_udp_packet' para ser o "cérebro" do servidor UDP
        udp_thread = threading.Thread(target=self.udpServer.Server, args=(self.handle_udp_packet,), daemon=True)
        
        # Thread para o servidor Multicast, que só envia os "pings" de descoberta
        discovery_thread = threading.Thread(target=self.multicastServer.Server, daemon=True)

        tcp_thread.start()
        udp_thread.start()
        discovery_thread.start()
        
        print("Gateway está online. Pressione Ctrl+C para sair.")
        try:
            while True:
                time.sleep(10) # Pausa o loop principal, as threads cuidam do trabalho
        except KeyboardInterrupt:
            print("\nEncerrando o Gateway...")

    def handle_udp_packet(self, data, addr):
        """
        Processa pacotes UDP recebidos. Esta é a porta de entrada para anúncios de dispositivos.
        """
        # Tenta decodificar como SmartCityMessage (padrão para Node.js e Python corrigido)
        try:
            message = messages_pb2.SmartCityMessage()
            message.ParseFromString(data)
            
            if message.HasField("devices"):
                device_info = message.devices
                print(f"[Gateway UDP] Anúncio envelopado recebido de {addr}: ID={device_info.device_id}")
                self.discovered_devices[device_info.device_id] = (device_info, addr)
                print(f"[Gateway] Dispositivo '{device_info.device_id}' adicionado/atualizado.")
                return

            elif message.HasField("sensor_data"):
                sensor_data = message.sensor_data
                print(f"[Gateway UDP] Dados de sensor de {sensor_data.device_id}: {sensor_data.value} {sensor_data.unit}")
                return

        except Exception:
            # Se falhou, pode ser um DeviceInfo "cru" (do dispositivo Python antigo)
            try:
                device_info = messages_pb2.DeviceInfo()
                device_info.ParseFromString(data)
                print(f"[Gateway UDP] Anúncio 'cru' (compatibilidade) recebido de {addr}: ID={device_info.device_id}")
                self.discovered_devices[device_info.device_id] = (device_info, addr)
                print(f"[Gateway] Dispositivo '{device_info.device_id}' adicionado/atualizado.")
            except Exception as e:
                print(f"[Gateway UDP] Pacote de {addr} não pôde ser decodificado: {e}")

    # --- FUNÇÕES MODIFICADAS PARA USAR A LISTA UNIFICADA ---

    def listarDispositivos(self):
        """
        CORRIGIDO: Lista os dispositivos do dicionário principal `self.discovered_devices`.
        """
        dispositivos = list(self.discovered_devices.values())
        
        if not dispositivos:
            return "--- Dispositivos Online ---\nNenhum dispositivo encontrado."

        linhas_resposta = "--- Dispositivos Online ---\n"
        # Cada item 'd' é uma tupla (device_info_obj, addr)
        for device_info_obj, addr in dispositivos:
           linhas_resposta += f'{device_info_obj.device_id}\n'
        return linhas_resposta
    
    def encontraDispositivo(self, tipo_int):
        """
        CORRIGIDO: Procura no dicionário principal `self.discovered_devices`.
        """
        # Itera sobre os valores (tuplas) do dicionário
        for device_info_obj, addr in self.discovered_devices.values():
            if device_info_obj.type == tipo_int:
                print(f"Dispositivo do tipo '{messages_pb2.DeviceType.Name(tipo_int)}' encontrado: {device_info_obj.device_id}")
                # Retorna a tupla completa (device_info, addr)
                return (device_info_obj, addr)
        
        print(f"Nenhum dispositivo do tipo '{messages_pb2.DeviceType.Name(tipo_int)}' foi encontrado.")
        return None

    # --- O RESTO DO CÓDIGO PERMANECE IGUAL ---
    # As funções abaixo não precisam de NENHUMA MUDANÇA, pois elas já usam as versões
    # corrigidas de 'listarDispositivos' e 'encontraDispositivo'.

    def handle_client_command(self, client_socket, client_address):
        """
        Este handler NÃO MUDA. Ele lida com os comandos do cliente TCP.
        """
        # ... (seu código de handle_client_command, sem nenhuma alteração) ...
        print(f"[Gateway] Lidando com o comando de {client_address}")
        try:
            command = client_socket.recv(1024).decode('utf-8').strip()
            parts = command.split(';')
            main_command = parts[0]
            
            resposta_para_cliente = "ERRO: Comando não processado."
            
            if main_command == 'LIGAR_DISPOSITIVO':
                tipo_dispositivo = int(parts[1])
                ligar = self.falsetrue(parts[2])
                device_info_tuple = self.encontraDispositivo(tipo_dispositivo)
                if device_info_tuple:
                    resposta_do_dispositivo = self.send_command_to_device(device_info_tuple[0], ligar=ligar)
                    resposta_para_cliente = resposta_do_dispositivo if resposta_do_dispositivo else f"ERRO: Falha ao comunicar com {device_info_tuple[0].device_id}."
                else:
                    resposta_para_cliente = f"ERRO: Nenhum dispositivo do tipo {tipo_dispositivo} encontrado."
            
            elif main_command == 'CONSULTAR_DISPOSITIVO':
                tipo_dispositivo = int(parts[1])
                consultar = self.falsetrue(parts[2])
                device_info_tuple = self.encontraDispositivo(tipo_dispositivo)
                if device_info_tuple:
                    resposta_do_dispositivo = self.send_command_to_device(device_info_tuple[0], consultar=consultar)
                    resposta_para_cliente = resposta_do_dispositivo if resposta_do_dispositivo else f"ERRO: Falha ao comunicar com {device_info_tuple[0].device_id}."
                else:
                    resposta_para_cliente = f"ERRO: Nenhum dispositivo do tipo {tipo_dispositivo} encontrado."

            elif main_command == "LISTAR_DISPOSITIVOS":
                resposta_para_cliente = self.listarDispositivos()
            
            else:
                resposta_para_cliente = "ERRO: Comando desconhecido."

            client_socket.sendall(resposta_para_cliente.encode('utf-8'))
        
        except Exception as e:
            print(f"[Gateway] Erro ao processar cliente: {e}")
        finally:
            client_socket.close()

    def send_command_to_device(self, device_info, ligar=True, consultar=None):
        """
        Esta função NÃO MUDA. Ela envia comandos para os atuadores.
        """
        # ... (seu código de send_command_to_device, sem nenhuma alteração) ...
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
                if not response_bytes:
                    return None
                return response_bytes.decode('utf-8')
        
        except socket.timeout:
            print(f"ERRO: Timeout ao esperar resposta do dispositivo {device_info.device_id}.")
            return None
        except Exception as e:
            print(f"ERRO ao se comunicar com o dispositivo {device_info.device_id}: {e}")
            return None
        
    def falsetrue(self, valor):
        """Esta função NÃO MUDA."""
        return valor.lower() == 'true'

if __name__ == "__main__":
    gw = Gateway()
    gw.start()