import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Cryptopunk Monitor", layout="wide", page_icon="🤖")

# --- DISFARCE DE NAVEGADOR (Anti-Bloqueio) ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- CSS CYBERPUNK (O Visual) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    /* Fundo Matrix */
    .stApp {
        background-color: #050505;
        background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Fontes Futuristas */
    h1, h2, h3, h4, .stMetricLabel, .stButton {
        font-family: 'Orbitron', sans-serif !important;
    }
    
    h1 { color: #00f3ff !important; text-shadow: 0 0 10px #00f3ff; }
    
    /* Cards Neon */
    div[data-testid="stMetric"] {
        background-color: #0e0e0e;
        border: 1px solid #00f3ff;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 0 5px rgba(0, 243, 255, 0.2);
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: #ff00ff;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.4);
        transform: scale(1.02);
        transition: all 0.3s ease;
    }
    
    /* Cores dos Textos */
    div[data-testid="stMetricLabel"] { color: #00f3ff !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ CRYPTOPUNK MONITOR")
st.markdown("---")

# --- SIDEBAR (Barra Lateral) ---
with st.sidebar:
    st.header("🛠️ Configuração")
    opcao = st.selectbox("Monitorar Ativo:", ["Bitcoin", "Ethereum", "Solana"])
    
    st.markdown("---")
    if st.button("🔄 Forçar Atualização"):
        st.rerun()
        
    st.markdown("---")
    st.caption("👨‍💻 **Desenvolvido por:**")
    st.markdown("**Kevem Hiago**") 
    st.caption("🚀 *Powered by Python*")

# --- MEMÓRIA (Session State) ---
if 'historico_btc' not in st.session_state: st.session_state['historico_btc'] = []
if 'historico_eth' not in st.session_state: st.session_state['historico_eth'] = []
if 'historico_sol' not in st.session_state: st.session_state['historico_sol'] = []

# --- FUNÇÕES BLINDADAS (Lógica Highlander v4) ---
def buscar_dados():
    # 1. Tenta CoinCap
    try:
        url = "https://api.coincap.io/v2/assets?ids=bitcoin,ethereum,solana"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        data = resp.json()['data']
        return {
            "BTC": float(data[0]['priceUsd']), 
            "ETH": float(data[1]['priceUsd']), 
            "SOL": float(data[2]['priceUsd']), 
            "Fonte": "CoinCap"
        }
    except: pass
    
    # 2. Tenta CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        data = resp.json()
        return {
            "BTC": data['bitcoin']['usd'], 
            "ETH": data['ethereum']['usd'], 
            "SOL": data['solana']['usd'], 
            "Fonte": "CoinGecko"
        }
    except: pass

    # 3. Tenta Binance (Última esperança)
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        data = resp.json()
        precos = {item['symbol']: float(item['price']) for item in data if item['symbol'] in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']}
        return {
            "BTC": precos['BTCUSDT'], 
            "ETH": precos['ETHUSDT'], 
            "SOL": precos['SOLUSDT'], 
            "Fonte": "Binance"
        }
    except: pass
    
    return None

# --- GRÁFICO NEON ---
def plot_grafico(historico, nome):
    df = pd.DataFrame(historico)
    
    # Define a cor baseada na moeda
    cor = "#00f3ff"
    if nome == "Bitcoin": cor = "#F7931A"
    elif nome == "Ethereum": cor = "#627EEA"
    elif nome == "Solana": cor = "#14F195"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Hora'], y=df['Preço'], mode='lines+markers',
        line=dict(color=cor, width=3),
        marker=dict(size=6, color="#fff", line=dict(width=2, color=cor))
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#00f3ff', family="Orbitron"),
        margin=dict(l=0, r=0, t=20, b=0), 
        height=350,
        xaxis=dict(showgrid=True, gridcolor='rgba(0,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,255,255,0.1)')
    )
    return fig

# --- LOOP PRINCIPAL ---
placeholder = st.empty()

while True:
    dados = buscar_dados()
    
    if dados:
        hora = datetime.now().strftime("%H:%M:%S")
        
        # Salva histórico
        st.session_state['historico_btc'].append({'Hora': hora, 'Preço': dados['BTC']})
        st.session_state['historico_eth'].append({'Hora': hora, 'Preço': dados['ETH']})
        st.session_state['historico_sol'].append({'Hora': hora, 'Preço': dados['SOL']})
        
        # Limita histórico para não pesar a memória (Mantém os últimos 40 pontos)
        for k in ['historico_btc', 'historico_eth', 'historico_sol']:
            if len(st.session_state[k]) > 40: st.session_state[k].pop(0)

        with placeholder.container():
            # Exibe as Métricas
            c1, c2, c3 = st.columns(3)
            c1.metric("BITCOIN", f"${dados['BTC']:,.2f}")
            c2.metric("ETHEREUM", f"${dados['ETH']:,.2f}")
            c3.metric("SOLANA", f"${dados['SOL']:,.2f}")
            
            # Exibe o Gráfico
            st.markdown(f"### 📉 Tendência: <span style='color:#ff00ff'>{opcao}</span>", unsafe_allow_html=True)
            chave = f"historico_{'btc' if opcao=='Bitcoin' else 'eth' if opcao=='Ethereum' else 'sol'}"
            
            if len(st.session_state[chave]) > 0:
                fig = plot_grafico(st.session_state[chave], opcao)
                st.plotly_chart(fig, use_container_width=True)
            
            st.caption(f"🟢 Fonte de Dados: **{dados['Fonte']}** | ⏱ Última atualização: {hora}")
            
    else:
        # Se tudo falhar, mostra aviso sem quebrar o site
        with placeholder.container():
            st.warning("⚠️ Instabilidade nas APIs. Reconectando em breve...")
    
    # ⏳ ESPERA 15 SEGUNDOS (Isso estabiliza o site)
    time.sleep(15)