# iniciar_semaforo.py
from dispositivos import Atuador

if __name__ == "__main__":
    semaforo = Atuador(tipo='TRAFFIC_LIGHT')
    semaforo.iniciar()