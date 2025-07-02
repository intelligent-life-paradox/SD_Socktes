class DispositivoContinuo{
     constructor(
        tipo
      ){
        this.device_id = this.gerarIdDispositivo(tipo)
        this.tipo = tipo
        this.ip = '127.0.0.1'
        this.port = 0
        this.estado = false
        this.is_actuator = false
    }

    multicast_dicovery(){
        const dgram = require('dgram')
        const socket = dgram.createSocket('udp4')
        
        const MULTICAST_ADDRESS = '224.1.1.1'
        const PORT = 5007
        
        socket.on('message', (msg, rinfo)=>   {
            console.log(`Recebendo messagens em ${rinfo.address}:${rinfo.port}: ${msg}`);
        }
        )
        socket.on('listening', () => {
            const address = socket.address();
            console.log(`Socket UDP escutando em ${address.address}:${address.port}`);
            socket.addMembership(MULTICAST_ADDRESS);
            console.log(`Juntando-se ao multicast: ${MULTICAST_ADDRESS}`);
        
        })
        
        socket.bind(PORT);
    }

   gerarIdDispositivo(tipo) {
  
        const tipoFormatado = tipo.toLowerCase().replace(/ /g, '_');

        const uuidCompleto = crypto.randomUUID();

        const uuidCurto = uuidCompleto.substring(0, 4);

        return `${tipoFormatado}_${uuidCurto}`;
}

}