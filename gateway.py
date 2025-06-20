''' O Gateway deve receber e enviar via tcp'''
#from protocols import tcpcliente, tcpserver
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