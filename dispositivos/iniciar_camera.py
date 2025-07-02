# iniciar_camera.py
from dispositivos import Atuador
import threading 
if __name__ == "__main__":
    thread = threading.Thread(target=Atuador(tipo='CAMERA').iniciar)
    thread.start()