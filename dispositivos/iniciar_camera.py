# iniciar_camera.py
from dispositivos import Atuador
if __name__ == "__main__":
    camera = Atuador(tipo='CAMERA')
    camera.iniciar()
    