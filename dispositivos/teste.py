from dispositivos import Continuos

if __name__ == "__main__":
    iniciar_sensor_temp = Continuos(tipo='TEMPERATURE_SENSOR', data_unit="Celsius")
    iniciar_sensor_temp.iniciar()