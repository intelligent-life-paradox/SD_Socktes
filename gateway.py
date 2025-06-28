''' O Gateway deve receber e enviar via tcp'''
import socket
from protos import todolist_pb2 as comunication

my_list = comunication.TodoList()
my_list.owner_id = 1234
my_list.owner_name = 'Tim'

first_item = my_list.todos.add()
first_item.state = comunication.TaskState.Value("TASK_DONE")
first_item.task = "Teste de ProtoBuf para o Python"
first_item.due_date = "31.10.2019"

print(my_list)

'''class gateway():
    def __init__():
        ...
    def gerenciar():
        ...
    def multicastUdp():
        ...
    def receber():
        ...
    def enviar():
        ...'''

class Gateway():
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Gateway iniciado em {self.host}:{self.port}")
    
    def receber(self):
        print("Aguardando conexão...")
        lista_recebida = comunication.TodoList()
         lista_recebida.ParseFromString(dados_bytes)

        print("\n### TODO LIST RECEBIDA ###")
        print(f"Owner ID: {lista_recebida.owner_id}")
        print(f"Owner Name: {lista_recebida.owner_name}")
        print("Tarefas:")
        for i, tarefa in enumerate(lista_recebida.todos):
            status = comunication.TaskState.Name(tarefa.state)
            print(f"  {i+1}. {tarefa.task} - Status: {status} - Até: {tarefa.due_date}")

        return lista_recebida