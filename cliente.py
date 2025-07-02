import socket
import time
from protos import messages_pb2 
# O endereço público do Gateway - a única coisa que o cliente precisa saber.
GATEWAY_IP = '127.0.0.1'
GATEWAY_TCP_PORT = 5009

def enviar_comando_para_gateway(comando, tipo= None, ligar = None, consultar = None):
    """
    Função que abre uma conexão, envia um comando e retorna a resposta.
    """
    if tipo is not None and ligar is None and consultar is None:
        comando = f"{comando};{tipo}"
    elif ligar is not None:
        comando = f"{comando};{tipo};{ligar}"
    elif consultar is not None:
        comando = f"{comando};{tipo};{consultar}"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((GATEWAY_IP, GATEWAY_TCP_PORT))
            
            s.sendall(comando.encode('utf-8'))
            
            resposta = s.recv(4096)
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
        tipo_map = {
                '1': messages_pb2.DeviceType.LIGHT_POST,
                '2': messages_pb2.DeviceType.TRAFFIC_LIGHT,
                '3': messages_pb2.DeviceType.CAMERA
            }
        input_usuario = input('Digite a opção desejada: ').lower().strip()
        
        if input_usuario == '1':
            dispositivo = input('Selecione o tipo de dispositivo a ser ligado (1=Poste, 2=Camera, 3=Semaforo): ').lower().strip()
            ligar = input(r'Ligar[1]\Desligar[0]: ').lower().strip()
            
            if ligar == '0':
                ligar = False
            else:
                ligar = True

            comando = 'LIGAR_DISPOSITIVO'
       
            if dispositivo in tipo_map:
                tipo = tipo_map[dispositivo]
                print(f"Enviando comando para ligar o tipo: {messages_pb2.DeviceType.Name(tipo)}")
                resposta_do_servidor = enviar_comando_para_gateway(comando, tipo, ligar)
                print(f"Resposta do Gateway: {resposta_do_servidor.decode('utf-8')}")
            else:
                print("Tipo de dispositivo inválido.")
        elif input_usuario == '2': 
            dispositivo = input('Selecione o dispositivo a ser consultado(1=Poste, 2=Camera, 3=Semaforo : ').lower().strip()
            comando = 'CONSULTAR_DISPOSITIVO'
            resposta_do_servidor = enviar_comando_para_gateway(comando)
            consultar = '1'
            if dispositivo in tipo_map:
                tipo = tipo_map[dispositivo]
                print(f"Enviando comando para consultar estado  {messages_pb2.DeviceType.Name(tipo)}")
                resposta_do_servidor = enviar_comando_para_gateway(comando, tipo, ligar =None, consultar = consultar)
                print(f"Resposta do Gateway: {resposta_do_servidor.decode('utf-8')}")
            else:
                print("Tipo de dispositivo inválido.")
        elif input_usuario == '3':
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