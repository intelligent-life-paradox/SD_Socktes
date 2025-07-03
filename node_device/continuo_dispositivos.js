const dgram = require('dgram');
const crypto = require('crypto');
const os = require('os');
const path = require('path');

// Caminho absoluto para o arquivo proto compilado
const protoPath = path.join(__dirname, '..', 'protos', 'messages_pb.js');
const messages = require(protoPath);

// Configurações de Rede
const MULTICAST_GROUP = '224.1.1.1';
const MULTICAST_PORT = 5007;
const GATEWAY_DATA_PORT = 5008;

class ContinuousDevice {
    constructor(tipoString, tipoEnum, dataUnit) {
        this.tipoString = tipoString;
        this.tipoEnum = tipoEnum;
        this.dataUnit = dataUnit;
        this.deviceId = `${this.tipoString.toLowerCase().replace(/ /g, '_')}_${crypto.randomUUID().substring(0, 4)}`;
        this.ip = this.getLocalIpAddress();
        console.log(`Dispositivo Node.js criado: ${this.deviceId}, IP: ${this.ip}`);
    }

    start() {
        console.log(`[${this.deviceId}] Iniciando serviços...`);
        this.listenForDiscovery();
        this.startSendingData();
    }

    listenForDiscovery() {
        const socket = dgram.createSocket({ type: 'udp4', reuseAddr: true });

        socket.on('error', (err) => {
            console.error(`[${this.deviceId}] Erro no socket de descoberta: ${err.stack}`);
            socket.close();
        });

        socket.on('message', (msg, rinfo) => {
            console.log(`\n[${this.deviceId}] Mensagem de descoberta recebida de ${rinfo.address}:${rinfo.port}`);
            // rinfo contém o endereço do Gateway
            this.sendAnnouncement(rinfo);
        });

        socket.on('listening', () => {
            socket.addMembership(MULTICAST_GROUP, this.ip);
            console.log(`[${this.deviceId}] Escutando por descoberta em ${MULTICAST_GROUP}:${MULTICAST_PORT}`);
        });

        socket.bind(MULTICAST_PORT);
    }
    
    sendAnnouncement(gatewayInfo) {
        const deviceInfoPayload = new messages.DeviceInfo();
        deviceInfoPayload.setDeviceId(this.deviceId);
        deviceInfoPayload.setType(this.tipoEnum);
        deviceInfoPayload.setIpAddress(this.ip);
        deviceInfoPayload.setIsActuator(false);
        deviceInfoPayload.setPort(0);

        const message = new messages.SmartCityMessage();
        
        message.setDevices(deviceInfoPayload); 

        const serializedMessage = message.serializeBinary();
        const responseSocket = dgram.createSocket('udp4');
        
        responseSocket.send(serializedMessage, GATEWAY_DATA_PORT, gatewayInfo.address, (err) => {
            if (err) {
                console.error(`[${this.deviceId}] Erro ao enviar anúncio:`, err);
            } else {
                console.log(`[${this.deviceId}] Anúncio envelopado enviado para ${gatewayInfo.address}:${GATEWAY_DATA_PORT}`);
            }
            responseSocket.close();
        });
    }

    startSendingData() {
        const dataSocket = dgram.createSocket('udp4');
        const gatewayIp = '127.0.0.1'; 

        setInterval(() => {
            const leitura = parseFloat((Math.random() * (35.0 - 18.0) + 18.0).toFixed(2));
            console.log(`[${this.deviceId}] Nova leitura: ${leitura} ${this.dataUnit}`);

            const sensorPayload = new messages.SensorData();
            sensorPayload.setDeviceId(this.deviceId);
            sensorPayload.setValue(leitura);
            sensorPayload.setUnit(this.dataUnit);
            
            const message = new messages.SmartCityMessage();
            message.setSensorData(sensorPayload);

            const serializedMessage = message.serializeBinary();
            dataSocket.send(serializedMessage, GATEWAY_DATA_PORT, gatewayIp, (err) => {
                if (err) console.error(`[${this.deviceId}] Erro ao enviar dados:`, err);
            });

        }, 15 * 1000);
    }

    getLocalIpAddress() {
        const interfaces = os.networkInterfaces();
        for (const name of Object.keys(interfaces)) {
            for (const iface of interfaces[name]) {
                if (iface.family === 'IPv4' && !iface.internal) return iface.address;
            }
        }
        return '127.0.0.1';
    }
}

if (require.main === module) {
    const sensor = new ContinuousDevice(
        "AIR QUALITY SENSOR",
        messages.DeviceType.AIR_QUALITY_SENSOR,
        "µg/m³"
    );
    sensor.start();
}