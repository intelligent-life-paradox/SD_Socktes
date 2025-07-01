# gateway.py
from protos import messages_pb2 
from protocols import tcp, udp, multicast
import threading
import time
import socket
class Gateway():
    def __init__(self):
       # Suas inicializações de servidor
       self.tcpServer = tcp.TCPServer('localhost', 5009, handler_function=self.handle_client_command)
       self.udpServer = udp.UDP('localhost', 5008)
       self.multicastServer = multicast.Mulicast()
       # Adicione um dicionário para manter os dispositivos descobertos
       self.discovered_devices = {}

    def start(self):
        """Inicia todos os serviços do gateway e os mantém rodando."""
        print("Gateway iniciando todos os serviços...")
        
        # Iniciar os servidores em threads "daemon" para que eles fechem
        # quando o programa principal terminar.
        tcp_thread = threading.Thread(target=self.tcpServer.Server, daemon=True)
        udp_thread = threading.Thread(target=self.udpServer.Server, daemon=True)
        
        # A descoberta pode ser uma função que roda uma vez ou continuamente
        # Vamos supor que ela roda continuamente para descobrir novos dispositivos
        discovery_thread = threading.Thread(target=self.multicastServer.Server, daemon=True)

        tcp_thread.start()
        udp_thread.start()
        discovery_thread.start()
        
        print("Gateway está online. Pressione Ctrl+C para sair.")
        try:
            # Mantém o thread principal vivo, esperando pelo encerramento
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nEncerrando o Gateway...")
    
    def handle_client_command(self, client_socket, client_address):
        """
        Este é o handler! Ele é chamado pelo TCPServer para cada cliente.
        Toda a sua lógica de roteamento de comandos vai aqui.
        """
        print(f"[Gateway] Lidando com o comando de {client_address}")
        try:
            command = client_socket.recv(1024).decode('utf-8').strip()
            parts = command.split(';')
            main_command = parts[0]
            
            resposta_para_cliente = "ERRO: Comando não processado."
            print(parts)
            if main_command == 'LIGAR_DISPOSITIVO' and len(parts) > 1:
                tipo_dispositivo = int(parts[1])
                ligar = self.falsetrue(parts[2])
                print(f'Comando para ligar/desligar dispositivo do tipo: {tipo_dispositivo}')
                
                device_info_tuple = self.encontraDispositivo(tipo_dispositivo)
                
                if device_info_tuple:
                    # Agora, esta função retorna a resposta do dispositivo ou None em caso de falha.
                    resposta_do_dispositivo = self.send_command_to_device(device_info_tuple[0], ligar)
                    
                    if resposta_do_dispositivo:
                        # Repassa a resposta do dispositivo diretamente para o cliente
                        resposta_para_cliente = resposta_do_dispositivo
                    else:
                        resposta_para_cliente = f"ERRO: Falha ao se comunicar com o dispositivo {device_info_tuple[0].device_id}."
                else:
                    resposta_para_cliente = f"ERRO: Nenhum dispositivo do tipo {tipo_dispositivo} encontrado."
            
            elif main_command == 'CONSULTAR_DISPOSITIVO':
                tipo_dispositivo = int(parts[1])
                consultar = self.falsetrue(parts[2])
                device_info_tuple = self.encontraDispositivo(tipo_dispositivo)
                if device_info_tuple:
                    resposta_do_dispositivo = self.send_command_to_device(device_info_tuple[0], consultar)
            elif main_command == "LISTAR_DISPOSITIVOS":
                resposta_para_cliente = self.listarDispositivos(self.multicastServer.getDevices())
            
            else:
                resposta_para_cliente = "ERRO: Comando desconhecido."

            client_socket.sendall(resposta_para_cliente.encode('utf-8'))
        
        except Exception as e:
            print(f"[Gateway] Erro ao processar cliente: {e}")
        finally:
            client_socket.close()


    def send_command_to_device(self, device_info, ligar=True, consultar = None):
        """
        Conecta-se a um dispositivo, envia um comando, ESPERA PELA RESPOSTA
        e a retorna.
        """
        try:
            device_ip = device_info.ip_address
            device_port = device_info.port

            print(f"Gateway: Conectando ao dispositivo {device_info.device_id} em {device_ip}:{device_port}...")
            if consultar is not None:
                command_payload = messages_pb2.Query(status= consultar)
                message_to_send = messages_pb2.SmartCityMessage(command=command_payload)
            else:
                command_payload = messages_pb2.Command(state=ligar)
                message_to_send = messages_pb2.SmartCityMessage(command=command_payload)
            serialized_message = message_to_send.SerializeToString()

            # O `with` ainda é bom para garantir o fechamento, mas agora faremos mais coisas dentro dele
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5) # Adiciona um timeout para não travar indefinidamente
                s.connect((device_ip, device_port))
                
                print(f"Gateway: Enviando comando para {device_info.device_id}.")
                s.sendall(serialized_message)
                
                print(f"Gateway: Aguardando resposta de {device_info.device_id}...")
                response_bytes = s.recv(1024)
                
                if not response_bytes:
                    print(f"Gateway: Dispositivo {device_info.device_id} fechou a conexão sem resposta.")
                    return None
                    
                response_str = response_bytes.decode('utf-8')
                print(f"Gateway: Resposta recebida de {device_info.device_id}:\n{response_str}")

                return response_str # Retorna a resposta decodificada
        
        except socket.timeout:
            print(f"ERRO: Timeout ao esperar resposta do dispositivo {device_info.device_id}.")
            return None
        except Exception as e:
            print(f"ERRO ao se comunicar com o dispositivo {device_info.device_id}: {e}")
            return None
        
    def listarDispositivos(self, dispositivos):
         linhas_resposta = "--- Dispositivos Online ---\n"
         for d in dispositivos:
           print(d[0].device_id)
           linhas_resposta+= f'{d[0].device_id}\n'
         return linhas_resposta
    
    
    # Remova o método ligarDispositivo, ele será substituído por send_command_to_device

    def encontraDispositivo(self, tipo_int):
        """
        Encontra o primeiro dispositivo de um certo tipo e retorna seu objeto DeviceInfo.
        """
        dispositivos = self.multicastServer.getDevices()
        for device_info in dispositivos:
            print(f'{device_info[0].device_id} -->{device_info[0].type}')
            if device_info[0].type == tipo_int:
                print(device_info)
                print(f"Dispositivo encontrado: {device_info}")
                return device_info # Retorna o objeto completo
        return None # Retorna None se não encontrar
    
    def falsetrue(self,valor):
        return valor.lower() == 'true'
         
# ... (outros métodos do gateway como 'listarDispositivos' etc. podem ficar aqui) ...

if __name__ == "__main__":
    gw = Gateway()
    gw.start()