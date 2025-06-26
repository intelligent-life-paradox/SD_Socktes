class Dispositivos():
    def __init__(self, tipo, ip, porta, estado)->None:
        self.tipo = tipo
        self.ip = ip
        self.porta = porta
        self.estado = estado
    
    def getEstado(self):
        return self.estado
    
    def setEstado(self, valor):
        self.estado =  valor

    def receber(msg):
        ...

    def enviar():
        ...
         
class Atuador(Dispositivos):
    
    def __init__(self):

        if self.tipo == 'Câmera':
             super.__init__('Câmera','224.5.6.7',12346, False)
        elif self.tipo =='Poste':
             super.__init__('Câmera','224.5.6.7',12347, False)
        elif self.tipo =='Semáforo':
             super.__init__('Semáforo','224.5.6.7',12348, False)
        
    def receberComando(self, comando):
        '''comando precisar ser transmitido via protobuffer''' 
        self.setEstado(comando)
        if self.getEstado() == True:
            print(f"Dispositivo {self.tipo} Ligado")
        else:
            print(f"Dispositivo {self.tipo} Ligado")

class Continuos(Dispositivos):
    def __init__(self):
        if self.tipo == 'Sensor_Ar':
             super.__init__('Sensor de Ar','224.5.6.7',12349, False)
        elif self.tipo =='Poste':
             super.__init__('Sensor de Temperatura','224.5.6.7',12350, False)

    def envio():
        ...