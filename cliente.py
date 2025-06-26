HOST='Localhost'
PORT=6789

#vamos criar o socket tcp para essa aplicação: 
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect((HOST, PORT))  # conecta ao servidor
    print("### CONTROLE DE COMANDOS ###")
    print()
    print('''
      Escolha uma opção para conseguir controlar os dispositivos
      [1] Ligar/Desligar Poste 
      [2] Mudar configuração de câmera
        - Alterar para FullHD
        - Alterar para HD
      [3] Mudar configuração de semáfaro
        - Alterar tempo de permanência como fechado
      [X] Sair da aplicação
    ''')
    while True:
        input_usuario = input('Digite a opção desejada: ').lower()
        if input_usuario == '1':
            id_poste = input('Digite o ID do poste(número inteiro): ')
            acao= input('Digite a ação desejada (ligar/desligar): ').lower()
            if acao in ['ligar', 'desligar']:
                comando = {
                    'id_poste': id_poste,
                    'acao': acao}
                cliente.sendall(json.dumps(comando).encode('utf-8'))
                resposta = cliente.recv(1024).decode('utf-8')
                print(f'Resposta do servidor: {resposta}')
            else:
                print('Ação inválida. Tente novamente.')
        elif input_usuario == '2':
            id_camera = input('Digite o ID da câmera(número inteiro): ')
            resolucao = input('Digite a resolução desejada (FullHD/HD): ').lower()
            if resolucao in ['fullhd', 'hd']:
                comando = {
                    'id_camera': id_camera,
                    'resolucao': resolucao}
                cliente.sendall(json.dumps(comando).encode('utf-8'))
                resposta = cliente.recv(1024).decode('utf-8')
                print(f'Resposta do servidor: {resposta}')
            else:
                print('Resolução inválida. Tente novamente.')
        elif input_usuario == '3':
            id_semaforo=input('Digite o ID do semáforo(número inteiro): ')
            tempo = input('Digite o tempo de permanência fechado (em segundos): ')
            if tempo.isdigit():
                tempo = int(tempo)
                comando = {'id_semaforo': id_semaforo, 'tempo_fechado': tempo}
                cliente.sendall(json.dumps(comando).encode('utf-8'))
                resposta = cliente.recv(1024).decode('utf-8')
                print(f'Resposta do servidor: {resposta}')
            else:
                print('Tempo inválido. Tente novamente.')
        elif input_usuario == 'x':
            print('Saindo da aplicação...')
            break   

    

