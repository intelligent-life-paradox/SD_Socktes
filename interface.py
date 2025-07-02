import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(layout="wide", page_title="Painel de Controle IoT")
st.title("Painel de Controle - Smart City IoT 🏙️")
st.markdown("Interface para monitoramento e controle de dispositivos conectados via Gateway.")

def obter_dados_sensores():
    temp = round(23.5 + np.random.randn() * 1.5, 1)
    qualidade_ar = int(45 + np.random.randn() * 5)
    return temp, qualidade_ar

# Inicializa históricos, se necessário
for nome, col in [("hist_temp", "Temperatura"), ("hist_ar", "Qualidade do Ar (AQI)")]:
    if nome not in st.session_state:
        st.session_state[nome] = pd.DataFrame(columns=[col])

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.header("🎮 Controle de Atuadores")
    st.markdown("---")

    with st.expander("📷 Câmera de Segurança", expanded=True):
        st.write("Status: **Online**")
        if st.button("Ver Feed ao Vivo"):
            st.toast("Iniciando streaming da câmera...")
            st.image("https://via.placeholder.com/300x200.png?text=Feed+da+Câmera",
                     caption="Simulação do feed da Câmera 1")

    with st.expander("💡 Poste de Iluminação", expanded=True):
        st.write("Status: **Online**")
        ligado = st.toggle("Ligar/Desligar Poste 1", value=True)
        st.success("O poste está LIGADO.") if ligado else st.warning("O poste está DESLIGADO.")

    with st.expander("🚦 Semáforo", expanded=True):
        st.write("Status: **Online**")
        modo_semaforo = st.radio(
            "Selecionar estado do Semáforo 1",
            ["Verde", "Amarelo", "Vermelho", "Modo Automático"],
            horizontal=True,
            index=3
        )
        st.info(f"Semáforo operando em: **{modo_semaforo}**")

with col2:
    st.header("📊 Monitoramento Central")
    st.markdown("---")

    st.subheader("Status do Gateway")
    st.success("✓ Conectado e Operacional")
    st.markdown("---")

    st.subheader("Sensores em Tempo Real")
    temp_atual, ar_atual = obter_dados_sensores()

    # Adiciona ao histórico
    st.session_state.hist_temp.loc[len(st.session_state.hist_temp)] = [temp_atual]
    st.session_state.hist_ar.loc[len(st.session_state.hist_ar)] = [ar_atual]

    for nome in ["hist_temp", "hist_ar"]:
        if len(st.session_state[nome]) > 20:
            st.session_state[nome] = st.session_state[nome].tail(20)

    st.metric("🌡️ Sensor de Temperatura", f"{temp_atual} °C", f"{round(temp_atual - 23.5, 1)} °C")
    st.metric("🌬️ Sensor de Qualidade do Ar (AQI)", f"{ar_atual}", f"{ar_atual - 45}", delta_color="inverse")
    st.markdown("---")

    st.subheader("Histórico de Dados")
    st.line_chart(st.session_state.hist_temp)
    st.line_chart(st.session_state.hist_ar)

with col3:
    st.header("📡 Gerenciamento de Dispositivos")
    st.markdown("---")

    if st.button("🔎 Buscar Novos Dispositivos na Rede"):
        with st.spinner("Procurando dispositivos... (Simulação de Multicast UDP)"):
            time.sleep(2)
        st.toast("Busca concluída! 1 novo dispositivo encontrado.")

    st.subheader("Dispositivos Conectados")
    dispositivos = {
        "Câmera 1": {"tipo": "Câmera", "status": "Online", "icon": "📷"},
        "Poste P-04": {"tipo": "Poste", "status": "Online", "icon": "💡"},
        "Semáforo S-01": {"tipo": "Semáforo", "status": "Online", "icon": "🚦"},
        "Sensor Temp-A": {"tipo": "Sensor de Temperatura", "status": "Online", "icon": "🌡️"},
        "Sensor Ar-A": {"tipo": "Sensor de Qualidade do Ar", "status": "Online", "icon": "🌬️"},
        "Câmera 2": {"tipo": "Câmera", "status": "Offline", "icon": "📷"},
    }

    for nome, info in dispositivos.items():
        status_func = st.success if info["status"] == "Online" else st.error
        status_func(f"{info['icon']} **{nome}** - Status: {info['status']}")

st.markdown("---")
st.text("Interface de exemplo desenvolvida com Streamlit.")


