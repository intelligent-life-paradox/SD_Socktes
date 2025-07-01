import socket
import time
from protos import messages_pb2 
# O endereço público do Gateway - a única coisa que o cliente precisa saber.
GATEWAY_IP = '127.0.0.1'
GATEWAY_TCP_PORT = 5009

def enviar_comando_para_gateway(comando, tipo= None ):
    """
    Função que abre uma conexão, envia um comando e retorna a resposta.
    """
    if tipo is not None:
        comando = str(comando) + ";" + str(tipo)
    # Usa 'with' para garantir que o socket seja sempre fechado
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((GATEWAY_IP, GATEWAY_TCP_PORT))
            
            # Envia o comando que recebemos como argumento
            s.sendall(comando.encode('utf-8'))
            
            # Espera por uma resposta (aumentar o buffer é uma boa prática)
            resposta = s.recv(4096)
            print(resposta)
            return resposta
            
    except ConnectionRefusedError:
        return "ERRO: Não foi possível conectar ao Gateway. Ele está online?"
    except Exception as e:
        return f"ERRO: Ocorreu um erro inesperado: {e}"


def menu_principal():
    print("### CONTROLE DA CIDADE INTELIGENTE ###")
    while True:
        print('''
      [1] Ligar/Desligar um dispositivo
            (1) Poste
            (2) Câmera
            (3) Semáforo
      [2] Consultar Estado dos Dispositivos        
      [3] Listar todos os dispositivos online
      [x] Sair
      ''')
        
        input_usuario = input('Digite a opção desejada: ').lower().strip()
        
        if input_usuario == '1':
            dispositivo = input('Selecione o tipo de dispositivo a ser ligado (1=Poste, 2=Camera, 3=Semaforo): ').lower().strip()
            comando = 'LIGAR_DISPOSITIVO'
   
            tipo_map = {
                '1': messages_pb2.DeviceType.LIGHT_POST,
                '2': messages_pb2.DeviceType.TRAFFIC_LIGHT,
                '3': messages_pb2.DeviceType.CAMERA
            }

            if dispositivo in tipo_map:
                tipo = tipo_map[dispositivo]
                print(f"Enviando comando para ligar o tipo: {messages_pb2.DeviceType.Name(tipo)}")
                resposta_do_servidor = enviar_comando_para_gateway(comando, tipo)
                print(f"Resposta do Gateway: {resposta_do_servidor.decode('utf-8')}")
            else:
                print("Tipo de dispositivo inválido.")

        elif input_usuario == '3': # A opção de listar é a 3 no seu menu
            comando = "LISTAR_DISPOSITIVOS" 
            print("\nSolicitando lista de dispositivos ao Gateway...")
            resposta_do_servidor = enviar_comando_para_gateway(comando)
            # A resposta já vem como bytes, então decodifique-a
            print("--- Resposta do Gateway ---")
            print(resposta_do_servidor.decode('utf-8'))
            print("---------------------------\n")

        elif input_usuario == 'x':
            break
if __name__ == "__main__":
    menu_principal()