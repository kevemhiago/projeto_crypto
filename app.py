import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Crypto Monitor Pro", layout="wide")
st.title("🪙 CryptoLive: Painel Multi-Moedas")

# --- MENU LATERAL ---
opcao = st.sidebar.selectbox("Escolha o Gráfico Principal:", ["Bitcoin", "Ethereum", "Solana"])

# --- MEMÓRIA (Session State) ---
if 'historico_btc' not in st.session_state: st.session_state['historico_btc'] = []
if 'historico_eth' not in st.session_state: st.session_state['historico_eth'] = []
if 'historico_sol' not in st.session_state: st.session_state['historico_sol'] = []

# --- FUNÇÃO DE BUSCA (AwesomeAPI) ---
def pegar_dados():
    # Busca BTC, ETH e SOL de uma vez só em Dólar
    url = "https://economia.awesomeapi.com.br/last/BTC-USD,ETH-USD,SOL-USD"
    try:
        response = requests.get(url)
        dados = response.json()
        return {
            "BTC": float(dados['BTCUSD']['bid']),
            "ETH": float(dados['ETHUSD']['bid']),
            "SOL": float(dados['SOLUSD']['bid'])
        }
    except:
        return None

# --- ÁREA DE ATUALIZAÇÃO ---
placeholder = st.empty()

# --- LOOP INFINITO ---
while True:
    precos = pegar_dados()
    
    if precos:
        hora = datetime.now().strftime("%H:%M:%S")

        # Salva nos históricos
        st.session_state['historico_btc'].append({'Hora': hora, 'Preço': precos['BTC']})
        st.session_state['historico_eth'].append({'Hora': hora, 'Preço': precos['ETH']})
        st.session_state['historico_sol'].append({'Hora': hora, 'Preço': precos['SOL']})

        # Mantém apenas os últimos 50 pontos para não pesar
        for moeda in ['historico_btc', 'historico_eth', 'historico_sol']:
            if len(st.session_state[moeda]) > 50:
                st.session_state[moeda].pop(0)

        # Desenha o Painel
        with placeholder.container():
            # KPIs
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("💰 Bitcoin", f"US$ {precos['BTC']:,.2f}")
            kpi2.metric("💎 Ethereum", f"US$ {precos['ETH']:,.2f}")
            kpi3.metric("🚀 Solana", f"US$ {precos['SOL']:,.2f}")

            # Gráfico
            st.markdown(f"### 📈 Tendência do {opcao}")
            if opcao == "Bitcoin": dados_grafico = st.session_state['historico_btc']
            elif opcao == "Ethereum": dados_grafico = st.session_state['historico_eth']
            else: dados_grafico = st.session_state['historico_sol']
            
            df = pd.DataFrame(dados_grafico)
            if not df.empty:
                st.line_chart(df.set_index('Hora')['Preço'], height=400)
    
    else:
        # Se der erro, avisa mas não quebra o site
        with placeholder.container():
            st.warning("⏳ Atualizando dados... (Aguarde um momento)")

    # Espera 5 segundos (Importante para não ser bloqueado de novo!)
    time.sleep(5)