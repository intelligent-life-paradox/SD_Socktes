# Simulação de Cidade Inteligente em Sistemas Distribuídos

Este projeto implementa um sistema distribuído que simula o funcionamento de uma cidade inteligente. A arquitetura é composta por um Gateway central, dispositivos IoT (atuadores e sensores) e um cliente de controle, todos se comunicando através de diferentes protocolos de rede e utilizando Protocol Buffers para a serialização de dados.


## 🏙️ Arquitetura do Sistema

O sistema é dividido em três componentes principais:

1.  **Gateway Central (Python):** Atua como o cérebro do sistema. Ele é responsável por:
    -   Descobrir dispositivos na rede usando um broadcast Multicast.
    -   Receber anúncios e dados periódicos de sensores via UDP.
    -   Expor uma interface TCP para receber comandos de um cliente.
    -   Rotear comandos para os atuadores corretos.

2.  **Dispositivos IoT (Python & Node.js):** Processos que simulam sensores e atuadores.
    -   **Atuadores (Python):** Simulam Postes de Luz, Semáforos e Câmeras. Eles possuem um servidor TCP para receber comandos de ligar/desligar do Gateway.
    -   **Sensores (Node.js & Python):** Simulam Sensores de Temperatura e de Qualidade do Ar. Eles enviam dados periodicamente (a cada 15 segundos) para o Gateway via UDP.

3.  **Cliente (Python):** Uma interface de linha de comando (CLI) que permite ao usuário final interagir com o sistema, enviando comandos para listar ou controlar os dispositivos através do Gateway.

## ⚙️ Tecnologias e Bibliotecas

| Componente                | Linguagem | Bibliotecas Principais                                        |
| ------------------------- | --------- | ------------------------------------------------------------- |
| **Gateway**               | Python    | `socket`, `threading`, `uuid`, `google-protobuf`              |
| **Dispositivos (Atuador)**| Python    | `socket`, `threading`, `uuid`, `google-protobuf`              |
| **Dispositivos (Sensor)** | Node.js   | `dgram`, `crypto`, `os`, `google-protobuf`                    |
| **Cliente**               | Python    | `socket`, `google-protobuf`                                   |

A comunicação e a estrutura de dados são padronizadas em todo o sistema utilizando **Protocol Buffers (Protobuf)**.

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e executar a simulação. É recomendado usar três terminais separados para visualizar os logs de cada componente.

### 1. Pré-requisitos

Certifique-se de ter o **Python 3** e o **Node.js** instalados em seu sistema.

**a) Instale as dependências Python:**

```bash
pip install protobuf
```

**b) Instale as dependências Node.js:**

Navegue até a pasta que contém o `package.json` do dispositivo Node.js e execute:

```bash
npm install google-protobuf
```

**c) Compile os arquivos Protocol Buffers:**

Você precisa compilar o arquivo `.proto` para ambas as linguagens. Execute os seguintes comandos a partir da raiz do projeto (`sd/`):

-   **Para Python:**
    ```bash
    protoc -I=. --python_out=. protos/messages.proto
    ```
-   **Para Node.js:**
    ```bash
    npm install -g grpc-tools
    grpc_tools_node_protoc --js_out=import_style=commonjs,binary:. -I=. protos/messages.proto
    ```

### 2. Iniciando os Componentes

**Terminal 1: Inicie os Dispositivos IoT**

Navegue até o diretório do projeto e execute o script que gerencia os dispositivos. Ele apresentará uma opção para iniciar em modo normal ou em modo de falha.

```bash
python dispositivos.py
```
Escolha a opção desejada (ex: `1` para o cenário normal). Os dispositivos começarão a escutar por mensagens de descoberta.

**Terminal 2: Inicie o Gateway Central**

O Gateway começará a enviar pings de descoberta e a escutar por anúncios de dispositivos e dados de sensores.

```bash
python gateway.py
```
Você verá os dispositivos sendo descobertos e adicionados à lista do Gateway.

**Terminal 3: Inicie o Cliente**

Com o Gateway e os dispositivos rodando, você pode iniciar o cliente para interagir com o sistema.

```bash
python cliente.py
```
Use o menu interativo para listar os dispositivos online e enviar comandos para ligar ou desligar os atuadores.

## 💬 Formato das Mensagens

Toda a comunicação entre Gateway e Dispositivos é padronizada via Protobuf. A comunicação entre Cliente e Gateway utiliza strings simples formatadas com `;`.

### Comunicação Cliente -> Gateway

-   **Listar Dispositivos:** `"LISTAR_DISPOSITIVOS"`
-   **Ligar/Desligar Atuador:** `"LIGAR_DISPOSITIVO;[TIPO];[ESTADO]"` (Ex: `"LIGAR_DISPOSITIVO;1;True"`)
-   **Consultar Atuador:** `"CONSULTAR_DISPOSITIVO;[TIPO];True"`

### Comunicação Gateway <-> Dispositivos

A comunicação via rede utiliza uma mensagem "envelope" `SmartCityMessage` que pode conter diferentes tipos de payload (`DeviceInfo`, `Command`, `SensorData`), conforme definido no arquivo `protos/messages.proto`. Isso permite um ponto de entrada único e flexível para o tratamento de dados no Gateway.

## 🔧 Observações e Melhorias

-   **Tratamento de Exceções:** O cliente foi aprimorado para lidar com `ConnectionRefusedError`, informando ao usuário quando o Gateway não está disponível.
-   **Interoperabilidade:** O sistema demonstra com sucesso a interoperabilidade entre componentes Python e Node.js através de protocolos de rede padrão (TCP/UDP) e um formato de serialização de dados comum (Protobuf).