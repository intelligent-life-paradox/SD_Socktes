import streamlit as st
import pandas as pd
import numpy as np
import time

# --- Configuração da Página ---
# Usamos o layout "wide" para aproveitar melhor o espaço da tela
st.set_page_config(layout="wide", page_title="Painel de Controle IoT")

# --- Título Principal ---
st.title("Painel de Controle - Smart City IoT 🏙️")
st.markdown("Interface para monitoramento e controle de dispositivos conectados via Gateway.")

# --- Simulação de Dados ---
# Em um cenário real, esses dados viriam de uma API, banco de dados ou diretamente dos dispositivos.
def obter_dados_sensores():
    """Função para simular a chegada de novos dados dos sensores."""
    temp = round(23.5 + np.random.randn() * 1.5, 1)
    qualidade_ar = int(45 + np.random.randn() * 5)
    return temp, qualidade_ar

# Inicializa o histórico de dados para o gráfico
if 'hist_temp' not in st.session_state:
    st.session_state.hist_temp = pd.DataFrame(columns=['Temperatura'])
if 'hist_ar' not in st.session_state:
    st.session_state.hist_ar = pd.DataFrame(columns=['Qualidade do Ar (AQI)'])


# --- Layout em 3 Colunas ---
col1, col2, col3 = st.columns(3, gap="large")


# --- COLUNA 1: CONTROLE DE ATUADORES ---
# (Representa o envio de requisições TCP/Protobuf para dispositivos de controle)
with col1:
    st.header("🎮 Controle de Atuadores")
    st.markdown("---")

    # Controle da Câmera
    with st.expander("📷 Câmera de Segurança", expanded=True):
        st.write("Status: **Online**")
        if st.button("Ver Feed ao Vivo"):
            st.toast("Iniciando streaming da câmera...")
            # Aqui iria o código para mostrar o vídeo
            st.image("https://via.placeholder.com/300x200.png?text=Feed+da+Câmera",
                     caption="Simulação do feed da Câmera 1")

    # Controle do Poste de Iluminação
    with st.expander("💡 Poste de Iluminação", expanded=True):
        st.write("Status: **Online**")
        ligado = st.toggle("Ligar/Desligar Poste 1", value=True)
        if ligado:
            st.success("O poste está LIGADO.")
        else:
            st.warning("O poste está DESLIGADO.")

    # Controle do Semáforo
    with st.expander("🚦 Semáforo", expanded=True):
        st.write("Status: **Online**")
        modo_semaforo = st.radio(
            "Selecionar estado do Semáforo 1",
            ["Verde", "Amarelo", "Vermelho", "Modo Automático"],
            horizontal=True,
            index=3
        )
        st.info(f"Semáforo operando em: **{modo_semaforo}**")


# --- COLUNA 2: MONITORAMENTO CENTRAL ---
# (Representa o recebimento periódico de dados dos sensores)
with col2:
    st.header("📊 Monitoramento Central")
    st.markdown("---")

    # Status do Gateway
    st.subheader("Status do Gateway")
    st.success("✓ Conectado e Operacional")
    st.markdown("---")

    # Métricas dos Sensores
    st.subheader("Sensores em Tempo Real")
    temp_atual, ar_atual = obter_dados_sensores()

    # Adiciona dados ao histórico
    st.session_state.hist_temp.loc[len(st.session_state.hist_temp)] = temp_atual
    st.session_state.hist_ar.loc[len(st.session_state.hist_ar)] = ar_atual
    
    # Limita o histórico para não sobrecarregar
    if len(st.session_state.hist_temp) > 20:
        st.session_state.hist_temp = st.session_state.hist_temp.tail(20)
    if len(st.session_state.hist_ar) > 20:
        st.session_state.hist_ar = st.session_state.hist_ar.tail(20)

    # Exibe as métricas
    st.metric(label="🌡️ Sensor de Temperatura", value=f"{temp_atual} °C", delta=f"{round(temp_atual - 23.5, 1)} °C")
    st.metric(label="🌬️ Sensor de Qualidade do Ar (AQI)", value=f"{ar_atual}", delta=f"{ar_atual - 45}", delta_color="inverse")
    st.markdown("---")

    # Gráfico de histórico
    st.subheader("Histórico de Dados")
    st.line_chart(st.session_state.hist_temp)
    st.line_chart(st.session_state.hist_ar)

# --- COLUNA 3: GERENCIAMENTO DE DISPOSITIVOS ---
# (Representa a descoberta de dispositivos via Multicast UDP)
with col3:
    st.header("📡 Gerenciamento de Dispositivos")
    st.markdown("---")
    
    # Botão para simular a descoberta
    if st.button("🔎 Buscar Novos Dispositivos na Rede"):
        with st.spinner("Procurando dispositivos... (Simulação de Multicast UDP)"):
            time.sleep(2) # Simula o tempo de espera da busca
        st.toast("Busca concluída! 1 novo dispositivo encontrado.")
        # Em um app real, aqui você atualizaria a lista de dispositivos
    
    st.subheader("Dispositivos Conectados")

    # Lista de dispositivos (simulada)
    dispositivos = {
        "Câmera 1": {"tipo": "Câmera", "status": "Online", "icon": "📷"},
        "Poste P-04": {"tipo": "Poste", "status": "Online", "icon": "💡"},
        "Semáforo S-01": {"tipo": "Semáforo", "status": "Online", "icon": "🚦"},
        "Sensor Temp-A": {"tipo": "Sensor de Temperatura", "status": "Online", "icon": "🌡️"},
        "Sensor Ar-A": {"tipo": "Sensor de Qualidade do Ar", "status": "Online", "icon": "🌬️"},
        "Câmera 2": {"tipo": "Câmera", "status": "Offline", "icon": "📷"},
    }

    for nome, info in dispositivos.items():
        if info["status"] == "Online":
            st.success(f"{info['icon']} **{nome}** - Status: {info['status']}")
        else:
            st.error(f"{info['icon']} **{nome}** - Status: {info['status']}")

# --- Rodapé ---
st.markdown("---")
st.text("Interface de exemplo desenvolvida com Streamlit.")

# Para atualizar os dados dos sensores periodicamente (simulação)
time.sleep(5)
st.rerun()