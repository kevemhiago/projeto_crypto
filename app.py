import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Crypto Monitor Pro", layout="wide")
st.title("🪙 CryptoLive: Painel Multi-Moedas")

# --- MENU LATERAL ---
# O usuário escolhe qual gráfico quer ver
opcao = st.sidebar.selectbox("Escolha o Gráfico Principal:", ["Bitcoin", "Ethereum", "Solana"])

# --- MEMÓRIA (Session State) ---
# Criamos uma memória separada para cada moeda
if 'historico_btc' not in st.session_state: st.session_state['historico_btc'] = []
if 'historico_eth' not in st.session_state: st.session_state['historico_eth'] = []
if 'historico_sol' not in st.session_state: st.session_state['historico_sol'] = []

# --- FUNÇÃO DE BUSCA ---
def pegar_preco(simbolo):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={simbolo}"
    resposta = requests.get(url)
    return float(resposta.json()['price'])

# --- ÁREA DE ATUALIZAÇÃO ---
placeholder = st.empty()

# --- LOOP INFINITO ---
while True:
    # 1. Busca os 3 preços ao mesmo tempo
    preco_btc = pegar_preco("BTCUSDT")
    preco_eth = pegar_preco("ETHUSDT")
    preco_sol = pegar_preco("SOLUSDT")
    
    hora = datetime.now().strftime("%H:%M:%S")

    # 2. Salva nos históricos
    st.session_state['historico_btc'].append({'Hora': hora, 'Preço': preco_btc})
    st.session_state['historico_eth'].append({'Hora': hora, 'Preço': preco_eth})
    st.session_state['historico_sol'].append({'Hora': hora, 'Preço': preco_sol})

    # Limpa dados antigos (mantém só os últimos 50 pontos)
    for moeda in ['historico_btc', 'historico_eth', 'historico_sol']:
        if len(st.session_state[moeda]) > 50:
            st.session_state[moeda].pop(0)

    # --- DESENHA A TELA ---
    with placeholder.container():
        # Linha 1: Os 3 Cartões (KPIs)
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("💰 Bitcoin", f"US$ {preco_btc:,.2f}")
        kpi2.metric("💎 Ethereum", f"US$ {preco_eth:,.2f}")
        kpi3.metric("🚀 Solana", f"US$ {preco_sol:,.2f}")

        # Linha 2: O Gráfico Selecionado
        st.markdown(f"### 📈 Tendência do {opcao}")
        
        # Decide qual histórico mostrar no gráfico baseado no Menu
        if opcao == "Bitcoin":
            dados_grafico = st.session_state['historico_btc']
        elif opcao == "Ethereum":
            dados_grafico = st.session_state['historico_eth']
        else:
            dados_grafico = st.session_state['historico_sol']
            
        df = pd.DataFrame(dados_grafico)
        if not df.empty:
            st.line_chart(df.set_index('Hora')['Preço'], height=400)

    time.sleep(1)