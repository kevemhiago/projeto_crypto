import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Cryptopunk Monitor", layout="wide", page_icon="🤖")

# --- CSS CYBERPUNK ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background-color: #050505;
        background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    h1, h2, h3, h4, .stMetricLabel {
        font-family: 'Orbitron', sans-serif !important;
    }
    
    h1 { color: #00f3ff !important; text-shadow: 0 0 10px #00f3ff; }
    
    div[data-testid="stMetric"] {
        background-color: #111;
        border: 1px solid #00f3ff;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.1);
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: #ff00ff;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ CRYPTOPUNK MONITOR")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🛠️ Painel de Controle")
    opcao = st.selectbox("Selecione o Ativo:", ["Bitcoin", "Ethereum", "Solana"])
    
    st.markdown("---")
    if st.button("🔄 Atualizar Manualmente"):
        st.rerun()
        
    st.markdown("---")
    st.caption("👨‍💻 **Desenvolvido por:**")
    st.markdown("**Kevem Hiago**") 
    st.caption("🚀 *Tech Stack: Python + Streamlit*")

# --- MEMÓRIA ---
if 'historico_btc' not in st.session_state: st.session_state['historico_btc'] = []
if 'historico_eth' not in st.session_state: st.session_state['historico_eth'] = []
if 'historico_sol' not in st.session_state: st.session_state['historico_sol'] = []

# --- FUNÇÕES BLINDADAS (Highlander) ---
def buscar_dados():
    # 1. Tenta CoinCap
    try:
        url = "https://api.coincap.io/v2/assets?ids=bitcoin,ethereum,solana"
        resp = requests.get(url, timeout=3)
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
        resp = requests.get(url, timeout=3)
        data = resp.json()
        return {
            "BTC": data['bitcoin']['usd'], 
            "ETH": data['ethereum']['usd'], 
            "SOL": data['solana']['usd'], 
            "Fonte": "CoinGecko"
        }
    except: pass
    
    return None

# --- GRÁFICO ---
def plot_grafico(historico, nome):
    df = pd.DataFrame(historico)
    cor = "#F7931A" if nome == "Bitcoin" else "#627EEA" if nome == "Ethereum" else "#14F195"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Hora'], y=df['Preço'], mode='lines+markers',
        line=dict(color=cor, width=3),
        marker=dict(size=6, color="#fff", line=dict(width=2, color=cor))
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#00f3ff', family="Orbitron"),
        margin=dict(l=0, r=0, t=20, b=0), height=350
    )
    return fig

# --- LOGICA PRINCIPAL ---
placeholder = st.empty()

while True:
    dados = buscar_dados()
    
    if dados:
        hora = datetime.now().strftime("%H:%M:%S")
        
        # Salva histórico
        st.session_state['historico_btc'].append({'Hora': hora, 'Preço': dados['BTC']})
        st.session_state['historico_eth'].append({'Hora': hora, 'Preço': dados['ETH']})
        st.session_state['historico_sol'].append({'Hora': hora, 'Preço': dados['SOL']})
        
        # Limita tamanho
        for k in ['historico_btc', 'historico_eth', 'historico_sol']:
            if len(st.session_state[k]) > 30: st.session_state[k].pop(0)

        with placeholder.container():
            # Métricas
            c1, c2, c3 = st.columns(3)
            c1.metric("BITCOIN", f"${dados['BTC']:,.2f}")
            c2.metric("ETHEREUM", f"${dados['ETH']:,.2f}")
            c3.metric("SOLANA", f"${dados['SOL']:,.2f}")
            
            # Gráfico
            st.markdown(f"### 📉 Análise: {opcao}")
            chave = f"historico_{'btc' if opcao=='Bitcoin' else 'eth' if opcao=='Ethereum' else 'sol'}"
            if len(st.session_state[chave]) > 0:
                fig = plot_grafico(st.session_state[chave], opcao)
                st.plotly_chart(fig, use_container_width=True)
            
            st.caption(f"🟢 Fonte: {dados['Fonte']} | Última atualização: {hora}")
            
    else:
        placeholder.error("⚠️ Tentando reconectar às APIs...")
        
    time.sleep(5)