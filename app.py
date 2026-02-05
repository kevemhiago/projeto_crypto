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

# --- FUNÇÃO DE BUSCA (Modo Espião 🕵️‍♂️) ---
def pegar_dados():
    url = "https://api.coincap.io/v2/assets?ids=bitcoin,ethereum,solana"
    
    # Cabeçalho para fingir que somos um navegador comum (Disfarce)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Avisa se der erro de conexão
        dados = response.json()['data']
        
        precos_dict = {}
        for item in dados:
            precos_dict[item['id']] = float(item['priceUsd'])
            
        return {
            "BTC": precos_dict['bitcoin'],
            "ETH": precos_dict['ethereum'],
            "SOL": precos_dict['solana']
        }
    except Exception as e:
        # Mostra o erro exato na tela para a gente descobrir o que é
        st.error(f"Ocorreu um erro: {e}")
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

        # Limpeza de memória
        for moeda in ['historico_btc', 'historico_eth', 'historico_sol']:
            if len(st.session_state[moeda]) > 50:
                st.session_state[moeda].pop(0)

        # Desenha o Painel
        with placeholder.container():
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
        # O erro já vai aparecer lá em cima pelo st.error
        time.sleep(1) # Espera curtinha para não travar
            
    # Intervalo
    time.sleep(10)