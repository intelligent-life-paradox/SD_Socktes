import socket
from protos import messages_pb2
class Mulicast():    
    
    def __init__(self):
        self.MCAST_GROUP = '224.1.1.1'
        self.MCAST_PORT = 5007
        self.msg = b'SERVICO_DISCOVERY_REQUEST' # precisa ser em protobuffer
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lista_ips_descobertos = []
    
            
    def getDevices(self):
        return self.lista_ips_descobertos
    
    def Client(self):

        self.sock.settimeout(5.0)

        self.sock.sendto(self.msg, (self.MCAST_GROUP,self.MCAST_PORT ))

        lista_ips_descobertos = [] # estes caras vão vir como protobuffer
        
        while True:
            try:
                dados, endereco_servidor = self.sock.recvfrom(1024)
                print(f"\nRecebi um resposta de {endereco_servidor}")
                resposta = dados.decode('utf-8')
                print(f'-> Mensagem: {resposta}')

                partes = resposta.split(';')
                if partes[0]=='SERVICE_RESPONSE':
                    servico_info = {'nome': partes[1], 'ip': partes[2], 'porta': endereco_servidor[1]}
                    print(f"  -> Serviço válido encontrado: {servico_info['nome']} no IP {servico_info['ip']}")
                    lista_ips_descobertos.append(servico_info)
                    
            except socket.timeout:
                # Se o tempo esgotou, o loop termina
                print("\nTempo de busca esgotado. A busca terminou.")
                break
            except Exception as e:
                print(f"Ocorreu um erro: {e}")
                break


        print("\n--- Resultado da Descoberta ---")
        if not lista_ips_descobertos:
            print("Nenhum serviço foi encontrado.")
        else:
            print(f"Total de serviços encontrados: {len(lista_ips_descobertos)}")
            for servico in lista_ips_descobertos:
                print(f"  - Nome: {servico['nome']}, Endereço: {servico['ip']}:{servico['porta']}")

        self.sock.close()
    def Server(self):
        # --- Configurações Comuns ---
        MCAST_GROUP = '224.1.1.1'
        MCAST_PORT = 5007
        SERVICE_NAME = "MeuServicoLegal-01"
        DISCOVERY_REQUEST_MSG = b'SERVICO_DISCOVERY_REQUEST' # Mensagem que o cliente envia

        print(f"Iniciando o serviço '{SERVICE_NAME}'...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ttl = 10       
        # Adiciona o timeout para que o socket não bloqueie para sempre (Corrige Ctrl+C)
        sock.settimeout(1.0)

        # 2. Liga o socket à porta e a todas as interfaces
        
        print(f"Serviço escutando na porta {MCAST_PORT}") # Corrigido para mostrar a porta
                 
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        sock.sendto(b'Tem alguem ai?', (MCAST_GROUP, MCAST_PORT))

        print(f"Serviço juntou-se ao grupo multicast {MCAST_GROUP}. Aguardando descobertas...")
        print("(Pressione Ctrl+C para sair)")

        # 4. Loop principal para escutar e responder
        while True:
            try:
                # Tenta receber dados (com timeout de 1s)
                dados, endereco_cliente = sock.recvfrom(1024)
                self.lista_ips_descobertos.append((messages_pb2.DeviceInfo.FromString(dados), endereco_cliente))
                #print(self.lista_ips_descobertos)
           
            except socket.timeout:
                # Timeout é esperado, apenas continue o loop
                continue
            
            except KeyboardInterrupt:
                print("\nServiço encerrado pelo usuário.")
                break
                
            except Exception as e:
                print(f'Ocorreu um erro: {e}')

        # Limpeza final
        print("Fechando o socket.")
        sock.close()