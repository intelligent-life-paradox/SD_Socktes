import socket
import struct

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