print("### CONTROLE DE COMANDOS ###")

print('''
      Escolha uma opção para conseguir controlar os dispositivos
      [1] Ligar/|Desligar Poste 
      [2] Mudar configuração de câmera
        - Alterar para FullHD
        - Alterar para HD
      [3] Mudar configuração de semáfaro
        - Alterar tempo de permanência como fechado
      [X] Sair da aplicação
      ''')

while True:
    entrada_usuario = input("Digite uma opção: ")
    if entrada_usuario == '1':
        ...
    elif entrada_usuario == '2':
        ...
    elif entrada_usuario == '3':
        ...
    elif entrada_usuario == 'x':
        print('Fechando aplicação!')
        break
    else:
        print("Digite uma opção válida")