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
                #print(self.multicastServer.getDevices())
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
            
            # --- MUDANÇA AQUI: SIMPLIFIQUE O PARSE DO COMANDO ---
            parts = command.split(';')
            main_command = parts[0]
            
            resposta_para_fcliente = "OK" # Resposta padrão de sucesso

            if main_command == 'LIGAR_DISPOSITIVO' and len(parts) > 1:
                tipo_dispositivo = int(parts[1])
                print(f'Comando para ligar dispositivo do tipo: {tipo_dispositivo}')
                
                device_info = self.encontraDispositivo(tipo_dispositivo)
                               
                try:
                    # Chame um novo método para enviar o comando para o dispositivo encontrado
                    success = self.send_command_to_device(device_info[0], ligar=True)
                    if not success:
                        resposta_para_cliente = "ERRO: Falha ao enviar comando para o dispositivo."
                    resposta_para_cliente = f'Dispostivo {device_info[0].device_id} ligado'   
                except:
                    resposta_para_cliente = f"ERRO: Nenhum dispositivo do tipo {tipo_dispositivo} encontrado."
                
                client_socket.sendall(resposta_para_cliente.encode('utf-8'))

            elif main_command == "LISTAR_DISPOSITIVOS":
                res = self.listarDispositivos(self.multicastServer.getDevices()) # Não precisa passar o argumento aqui
                client_socket.sendall(res.encode('utf-8'))
                 
            else:
                client_socket.sendall(b"ERRO: Comando desconhecido.")
        
        except Exception as e:
            print(f"[Gateway] Erro ao processar cliente: {e}")
        finally:
            client_socket.close()

    def send_command_to_device(self, device_info, ligar=True):
        """
        Conecta-se a um dispositivo específico via TCP e envia um comando.
        """
        try:
            # Pega o IP e a porta do dispositivo que descobrimos
            device_ip = device_info.ip_address
            device_port = device_info.port

            print(f"Tentando conectar ao dispositivo {device_info.device_id} em {device_ip}:{device_port}...")

            command_payload = messages_pb2.Command(state=ligar)
            message_to_send = messages_pb2.SmartCityMessage(command=command_payload)
            
            # Serializa a mensagem para enviar
            serialized_message = message_to_send.SerializeToString()

            # Cria um NOVO socket para falar com o dispositivo
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((device_ip, device_port))
                s.sendall(serialized_message)
                print(f"Comando enviado com sucesso para {device_info.device_id}.")
            return True

        except Exception as e:
            print(f"ERRO ao se comunicar com o dispositivo {device_info.device_id}: {e}")
            return False
        
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
# ... (outros métodos do gateway como 'listarDispositivos' etc. podem ficar aqui) ...

if __name__ == "__main__":
    gw = Gateway()
    gw.start()