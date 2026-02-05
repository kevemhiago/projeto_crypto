import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Cryptopunk Monitor", layout="wide", page_icon="🤖")

# --- CSS CYBERPUNK (O Segredo do Visual) ---
st.markdown("""
<style>
    /* Importando fonte futurista */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    /* Fundo Geral */
    .stApp {
        background-color: #050505;
        background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
    }

    /* Títulos */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00f3ff !important;
        text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff;
    }

    /* Cards de KPI (Métricas) */
    div[data-testid="stMetric"] {
        background-color: #111;
        border: 1px solid #00f3ff;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.6);
        border-color: #ff00ff;
    }

    /* Texto das Métricas */
    div[data-testid="stMetricLabel"] {
        color: #ff00ff !important;
        font-family: 'Orbitron', sans-serif;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 0 0 5px #ffffff;
    }

    /* Botões e Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }
    
</style>
""", unsafe_allow_html=True)

st.title("⚡ CRYPTOPUNK LIVE MONITOR")
st.markdown("---")

# --- MENU LATERAL ---
st.sidebar.title("🛠️ Config")
opcao = st.sidebar.selectbox("Rastrear Ativo:", ["Bitcoin", "Ethereum", "Solana"])
st.sidebar.markdown("---")
st.sidebar.caption("📡 Status: **ONLINE**")
st.sidebar.caption("🔗 Rede: **SECURE**")

# --- MEMÓRIA ---
if 'historico_btc' not in st.session_state: st.session_state['historico_btc'] = []
if 'historico_eth' not in st.session_state: st.session_state['historico_eth'] = []
if 'historico_sol' not in st.session_state: st.session_state['historico_sol'] = []

# --- FUNÇÕES DE BUSCA (Mantendo a lógica Highlander) ---
def buscar_coincap():
    try:
        url = "https://api.coincap.io/v2/assets?ids=bitcoin,ethereum,solana"
        response = requests.get(url, timeout=5)
        dados = response.json()['data']
        precos = {item['id']: float(item['priceUsd']) for item in dados}
        return {"BTC": precos['bitcoin'], "ETH": precos['ethereum'], "SOL": precos['solana'], "Fonte": "CoinCap"}
    except: return None

def buscar_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        dados = response.json()
        return {"BTC": dados['bitcoin']['usd'], "ETH": dados['ethereum']['usd'], "SOL": dados['solana']['usd'], "Fonte": "CoinGecko"}
    except: return None

def buscar_binance():
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, timeout=5)
        dados = response.json()
        precos = {item['symbol']: float(item['price']) for item in dados if item['symbol'] in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']}
        return {"BTC": precos['BTCUSDT'], "ETH": precos['ETHUSDT'], "SOL": precos['SOLUSDT'], "Fonte": "Binance"}
    except: return None

def pegar_dados_inteligente():
    dados = buscar_coincap()
    if dados: return dados
    dados = buscar_coingecko()
    if dados: return dados
    dados = buscar_binance()
    if dados: return dados
    return None

# --- FUNÇÃO DO GRÁFICO NEON ---
def criar_grafico_neon(dados_historico, moeda_nome):
    df = pd.DataFrame(dados_historico)
    
    # Cores baseadas na moeda
    cor_linha = "#00f3ff" # Ciano Padrão
    if moeda_nome == "Bitcoin": cor_linha = "#F7931A" # Laranja BTC
    elif moeda_nome == "Ethereum": cor_linha = "#627EEA" # Azul ETH
    elif moeda_nome == "Solana": cor_linha = "#14F195" # Verde SOL

    fig = go.Figure()
    
    # Adiciona a linha brilhante
    fig.add_trace(go.Scatter(
        x=df['Hora'], 
        y=df['Preço'],
        mode='lines+markers',
        line=dict(color=cor_linha, width=3),
        marker=dict(size=6, color="#ffffff", line=dict(width=2, color=cor_linha)),
        name=moeda_nome
    ))

    # Estilização Cyberpunk do Layout do Gráfico
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#00f3ff', family="Orbitron"),
        xaxis=dict(showgrid=True, gridcolor='rgba(0, 243, 255, 0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0, 243, 255, 0.1)', tickprefix="$"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=400,
        hovermode="x unified"
    )
    
    return fig

# --- ÁREA DE ATUALIZAÇÃO ---
placeholder = st.empty()

while True:
    dados_api = pegar_dados_inteligente()
    
    if dados_api:
        hora = datetime.now().strftime("%H:%M:%S")
        precos = dados_api

        st.session_state['historico_btc'].append({'Hora': hora, 'Preço': precos['BTC']})
        st.session_state['historico_eth'].append({'Hora': hora, 'Preço': precos['ETH']})
        st.session_state['historico_sol'].append({'Hora': hora, 'Preço': precos['SOL']})

        # Limpeza
        for moeda in ['historico_btc', 'historico_eth', 'historico_sol']:
            if len(st.session_state[moeda]) > 40:
                st.session_state[moeda].pop(0)

        with placeholder.container():
            # KPIs Estilizados
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("BITCOIN", f"${precos['BTC']:,.2f}")
            kpi2.metric("ETHEREUM", f"${precos['ETH']:,.2f}")
            kpi3.metric("SOLANA", f"${precos['SOL']:,.2f}")

            # Seleciona dados para o gráfico
            st.markdown(f"### 📉 ANÁLISE EM TEMPO REAL: <span style='color:#ff00ff'>{opcao.upper()}</span>", unsafe_allow_html=True)
            
            if opcao == "Bitcoin": 
                dados_grafico = st.session_state['historico_btc']
            elif opcao == "Ethereum": 
                dados_grafico = st.session_state['historico_eth']
            else: 
                dados_grafico = st.session_state['historico_sol']
            
            if len(dados_grafico) > 0:
                fig = criar_grafico_neon(dados_grafico, opcao)
                st.plotly_chart(fig, use_container_width=True)
            
            st.caption(f"💾 Fonte de Dados: {precos['Fonte']} | ⏱ Atualização: {hora}")

    else:
        with placeholder.container():
            st.error("⚠️ SYSTEM FAILURE: Sem conexão com APIs.")
            
    time.sleep(5)