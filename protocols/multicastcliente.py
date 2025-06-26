import socket
import struct


class Mulicast():
    def __init__(self):
        self.MCAST_GROUP = '224.5.6.7'
        self.MCAST_PORT = 12345
        self.msg = b'SERVICO_DISCOVERY_REQUEST' # precisa ser em protobuffer
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def Client(self):

        self.sock.settimeout(5.0)

        self.sock.sendto(self.msg, (self.MCAST_GROUP,self.MCAST_PORT ))

        lista_ips_descobertos = []
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
    def Server():
        # --- Configurações Comuns ---
        MCAST_GROUP = '224.5.6.7'
        MCAST_PORT = 12345
        SERVICE_NAME = "MeuServicoLegal-01"
        DISCOVERY_REQUEST_MSG = b'SERVICO_DISCOVERY_REQUEST' # Mensagem que o cliente envia

        print(f"Iniciando o serviço '{SERVICE_NAME}'...")

        # 1. Cria um socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Permite que múltiplos sockets escutem na mesma porta
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Adiciona o timeout para que o socket não bloqueie para sempre (Corrige Ctrl+C)
        sock.settimeout(1.0)

        # 2. Liga o socket à porta e a todas as interfaces
        sock.bind(('', MCAST_PORT))
        print(f"Serviço escutando na porta {MCAST_PORT}") # Corrigido para mostrar a porta

        # 3. Junta-se ao grupo multicast
        group = socket.inet_aton(MCAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"Serviço juntou-se ao grupo multicast {MCAST_GROUP}. Aguardando descobertas...")
        print("(Pressione Ctrl+C para sair)")

        # 4. Loop principal para escutar e responder
        while True:
            try:
                # Tenta receber dados (com timeout de 1s)
                dados, endereco_cliente = sock.recvfrom(1024)

                # Se recebeu algo, verifica se é a mensagem correta
                if dados == DISCOVERY_REQUEST_MSG: # Corrigido para usar a mensagem correta
                    print(f"\nRecebido pedido de descoberta de {endereco_cliente}")
                    print(" -> É um pedido de descoberta! Preparando resposta...")

                    meu_ip = socket.gethostbyname(socket.gethostname())
                    resposta = f"SERVICE_RESPONSE;{SERVICE_NAME};{meu_ip}"
                    
                    sock.sendto(resposta.encode('utf-8'), endereco_cliente)
                    print(f' -> Resposta enviada para {endereco_cliente}')
            
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