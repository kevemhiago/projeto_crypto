import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Crypto Monitor Pro", layout="wide")
st.title("🪙 CryptoLive: Painel Multi-Moedas (Blindado)")

# --- MENU LATERAL ---
opcao = st.sidebar.selectbox("Escolha o Gráfico Principal:", ["Bitcoin", "Ethereum", "Solana"])

# --- MEMÓRIA (Session State) ---
if 'historico_btc' not in st.session_state: st.session_state['historico_btc'] = []
if 'historico_eth' not in st.session_state: st.session_state['historico_eth'] = []
if 'historico_sol' not in st.session_state: st.session_state['historico_sol'] = []

# --- FUNÇÃO 1: COINCAP (Principal) ---
def buscar_coincap():
    try:
        url = "https://api.coincap.io/v2/assets?ids=bitcoin,ethereum,solana"
        response = requests.get(url, timeout=5)
        dados = response.json()['data']
        precos = {item['id']: float(item['priceUsd']) for item in dados}
        return {"BTC": precos['bitcoin'], "ETH": precos['ethereum'], "SOL": precos['solana'], "Fonte": "CoinCap"}
    except:
        return None

# --- FUNÇÃO 2: COINGECKO (Reserva) ---
def buscar_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        dados = response.json()
        return {"BTC": dados['bitcoin']['usd'], "ETH": dados['ethereum']['usd'], "SOL": dados['solana']['usd'], "Fonte": "CoinGecko"}
    except:
        return None

# --- FUNÇÃO 3: BINANCE (Último Recurso) ---
def buscar_binance():
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, timeout=5)
        dados = response.json()
        precos = {item['symbol']: float(item['price']) for item in dados if item['symbol'] in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']}
        return {"BTC": precos['BTCUSDT'], "ETH": precos['ETHUSDT'], "SOL": precos['SOLUSDT'], "Fonte": "Binance"}
    except:
        return None

# --- GERENCIADOR DE FONTES ---
def pegar_dados_inteligente():
    # Tenta na ordem: CoinCap -> CoinGecko -> Binance
    dados = buscar_coincap()
    if dados: return dados
    
    dados = buscar_coingecko()
    if dados: return dados
    
    dados = buscar_binance()
    if dados: return dados
    
    return None

# --- ÁREA DE ATUALIZAÇÃO ---
placeholder = st.empty()

# --- LOOP INFINITO ---
while True:
    dados_api = pegar_dados_inteligente()
    
    if dados_api:
        hora = datetime.now().strftime("%H:%M:%S")
        precos = dados_api # Simplificar nome

        # Salva nos históricos
        st.session_state['historico_btc'].append({'Hora': hora, 'Preço': precos['BTC']})
        st.session_state['historico_eth'].append({'Hora': hora, 'Preço': precos['ETH']})
        st.session_state['historico_sol'].append({'Hora': hora, 'Preço': precos['SOL']})

        # Limpeza de memória
        for moeda in ['historico_btc', 'historico_eth', 'historico_sol']:
            if len(st.session_state[moeda]) > 50:
                st.session_state[moeda].pop(0)

        # Desenha o Painel
        with placeholder.container():
            # Mostra qual API está salvando a pátria
            st.caption(f"🟢 Dados recebidos via: **{precos['Fonte']}**")
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("💰 Bitcoin", f"US$ {precos['BTC']:,.2f}")
            kpi2.metric("💎 Ethereum", f"US$ {precos['ETH']:,.2f}")
            kpi3.metric("🚀 Solana", f"US$ {precos['SOL']:,.2f}")

            st.markdown(f"### 📈 Tendência do {opcao}")
            if opcao == "Bitcoin": dados_grafico = st.session_state['historico_btc']
            elif opcao == "Ethereum": dados_grafico = st.session_state['historico_eth']
            else: dados_grafico = st.session_state['historico_sol']
            
            df = pd.DataFrame(dados_grafico)
            if not df.empty:
                st.line_chart(df.set_index('Hora')['Preço'], height=400)
    
    else:
        with placeholder.container():
            st.error("⚠️ Todas as APIs falharam. Verifique sua conexão.")
            
    time.sleep(10)