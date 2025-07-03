# Em protocols/tcp.py

import socket
import threading

class TCPServer():
    def __init__(self, ip, porta, handler_function):
        """
        Inicializa o servidor TCP.
        :param ip: O endereço IP para escutar.
        :param porta: A porta para escutar.
        :param handler_function: A função que será chamada para lidar com cada cliente.
                                  Esta função deve aceitar (socket, address) como argumentos.
        """
        self.ip = ip
        self.porta = porta
        self.handler = handler_function 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def Server(self):
        """
        Inicia o loop principal do servidor para aceitar conexões.
        """
        try:
            self.server_socket.bind((self.ip, self.porta))
            self.server_socket.listen(5) 
            print(f"[TCPServer] Escutando em {self.ip}:{self.porta}")

            while True:
                client_conn, client_addr = self.server_socket.accept()
                print(f"[TCPServer] Nova conexão aceita de {client_addr}")

                client_thread = threading.Thread(
                    target=self.handler, 
                    args=(client_conn, client_addr)
                )
                client_thread.daemon = True 
                client_thread.start()

        except KeyboardInterrupt:
            print("\n[TCPServer] Comando de encerramento recebido.")
        except Exception as e:
            print(f"[TCPServer] Ocorreu um erro crítico: {e}")
        finally:
            print("[TCPServer] Fechando o soquete do servidor.")
            self.server_socket.close()