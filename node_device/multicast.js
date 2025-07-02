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