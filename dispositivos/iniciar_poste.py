# iniciar_poste.py
from dispositivos import Atuador

if __name__ == "__main__":
    poste = Atuador(tipo='LAMP_POST')
    
    # Inicia o dispositivo. Ele cuidará de toda a lógica de rede a partir daqui.
    poste.iniciar()