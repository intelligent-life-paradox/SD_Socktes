# udp_listener.py
import socket

GATEWAY_IP = '127.0.0.1'  # ou '0.0.0.0' para escutar em todas as interfaces
GATEWAY_DATA_PORT = 5008

# Cria um socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liga o socket ao endereço e porta
sock.bind((GATEWAY_IP, GATEWAY_DATA_PORT))

print(f"--- Escutador UDP Simples ---")
print(f"Ouvindo em {GATEWAY_IP}:{GATEWAY_DATA_PORT}...")
print("Inicie seu Gateway e depois seus dispositivos. Qualquer pacote UDP para esta porta será mostrado aqui.")
print("Pressione Ctrl+C para sair.")

try:
    while True:
        # Espera por um pacote
        data, addr = sock.recvfrom(1024)
        
        print("\n-----------------------------------------")
        print(f"PACOTE RECEBIDO de: {addr}")
        print(f"Tamanho do pacote: {len(data)} bytes")
        print(f"Dados brutos (bytes): {data}")
        print("-----------------------------------------")

except KeyboardInterrupt:
    print("\nEncerrando o escutador.")
finally:
    sock.close()