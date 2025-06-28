# iniciar_sensor_temp.py
from dispositivos import Continuos

if __name__ == "__main__":
    sensor_temp = Continuos(tipo='TEMPERATURE_SENSOR', data_unit="Celsius")
    sensor_temp.iniciar()