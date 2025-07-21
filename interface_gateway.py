import streamlit as st
from cliente import enviar_comando_para_gateway

# Mapeamento fixo dos tipos de dispositivo (valores inteiros do protobuf)
TIPOS_DISPOSITIVO = {
    "Poste de Iluminação": 1,
    "Semáforo": 2,
    "Câmera de Segurança": 3
}

st.set_page_config(layout="wide", page_title="Painel Gateway IoT")
st.title("🌐 Interface Real - Dispositivos da Cidade Inteligente")
st.markdown("Interface conectada ao Gateway via TCP para controle em tempo real.")

#  dispositivos online
st.subheader("📡 Dispositivos Online")
lista_raw = enviar_comando_para_gateway("LISTAR_DISPOSITIVOS")
lista_formatada = lista_raw.splitlines()

if "ERRO" in lista_formatada[0]:
    st.error(lista_formatada[0])
else:
    for linha in lista_formatada[1:]:
        st.success(f"🟢 {linha}")

st.divider()

# Controle e consulta
st.subheader("⚙️ Controle de Dispositivos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔌 Ligar/Desligar")
    for nome, tipo in TIPOS_DISPOSITIVO.items():
        ligado = st.toggle(f"{nome} - Ligar/Desligar")
        if st.button(f"Aplicar: {nome}"):
            comando = "LIGAR_DISPOSITIVO"
            resposta = enviar_comando_para_gateway(comando, tipo=tipo, ligar=ligado)
            st.toast(resposta.decode('utf-8'))

with col2:
    st.markdown("### 🔍 Consultar Estado")
    for nome, tipo in TIPOS_DISPOSITIVO.items():
        if st.button(f"Consultar: {nome}"):
            comando = "CONSULTAR_DISPOSITIVO"
            resposta = enviar_comando_para_gateway(comando, tipo=tipo, consultar='true')
            st.info(resposta.decode('utf-8'))

st.caption("Interface operando com base na comunicação TCP com Gateway.")
