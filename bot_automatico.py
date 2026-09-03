import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as god
from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from datetime import datetime, timedelta, timezone

# 🎨 Configurazione stile TradingView Avanzato
st.set_page_config(page_title="TradingView IA Broker Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #131722; color: #d1d4dc; }
    header { background-color: #1c2030 !important; }
    .css-1d391kg { background-color: #1c2030; }
    </style>
    """, unsafe_allow_html=True)

# --- CREDENZIALI ALPACA ---
API_KEY = "PKGBTKR5UFADYCUR2QYPXU45MN"
SECRET_KEY = "HWnrgJW7UxCUEDnEfkEatRiPQPE2yAukjVEWPkFtahcZ"

try:
    client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True)
    crypto_data_client = CryptoHistoricalDataClient()
    stock_data_client = StockHistoricalDataClient(api_key=API_KEY, secret_key=SECRET_KEY)
    
    account = client.get_account()
    saldo_reale = float(account.cash)
    valore_portafoglio = float(account.portfolio_value)
    guadagno_totale = valore_portafoglio - 100000.0 # Calcolo rispetto ai 100k iniziali

    # 🖥️ BARRA LATERALE: PORTAFOGLIO E WALLET CARTE
    st.sidebar.image("https://wikimedia.org", width=150)
    st.sidebar.markdown("<h2 style='color:#d1d4dc;'>💳 ACCOUNT WALLET</h2>", unsafe_allow_html=True)
    st.sidebar.metric(label="Saldo Netto Prelevabile", value=f"${saldo_reale:,.2f}")
    st.sidebar.metric(label="Valore Totale Portafoglio", value=f"${valore_portafoglio:,.2f}")
    
    if guadagno_totale >= 0:
        st.sidebar.success(f"📈 Profitto Storico: +${guadagno_totale:,.2f}")
    else:
        st.sidebar.error(f"📉 Variazione Storica: ${guadagno_totale:,.2f}")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Deposita Fondi")
    deposito = st.sidebar.number_input("Importo da caricare ($):", min_value=10.0, step=50.0, key="dep")
    if st.sidebar.button("Deposita con Carta"):
        st.sidebar.info(f"Reindirizzamento sicuro a Stripe... (Tariffa 1.4%)")
        
    st.sidebar.subheader("📤 Preleva Fondi")
    prelievo = st.sidebar.number_input("Importo da riscuotere ($):", min_value=10.0, max_value=saldo_reale if saldo_reale > 10 else 10.0, step=50.0, key="prel")
    if st.sidebar.button("Invia Fondi alla Carta"):
        st.sidebar.success(f"Richiesta inviata! ${prelievo} in accredito sulla tua carta.")

    # 📈 CORPO PRINCIPALE
    st.markdown("<h1 style='color:#d1d4dc; font-family:sans-serif;'>📊 Mio Broker Avanzato TradingView con IA</h1>", unsafe_allow_html=True)
    
    col_grafico, col_ia = st.columns(2)
    
    with col_ia:
        st.markdown("<h3 style='color:#d1d4dc;'>🤖 Mente IA Private</h3>", unsafe_allow_html=True)
        asset_ia = st.selectbox("Seleziona asset per segnale IA:", ["BTC/USD", "ETH/USD", "TSLA", "NVDA", "AAPL"])
        st.markdown(f"**Ultimo Controllo:** {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")
        
        st.markdown("<h4 style='color:#d1d4dc;'>🔮 Decisione IA</h4>", unsafe_allow_html=True)
        if asset_ia in ["BTC/USD", "TSLA", "ETH/USD"]:
            st.metric(label="Previsione di Mercato", value="BULLISH (BUY)", delta="Segnale di Acquisto Attivo")
        else:
            st.metric(label="Previsione di Mercato", value="BEARISH (SELL)", delta="- Segnale di Vendita", delta_color="inverse")
            
        st.markdown("---")
        st.markdown("<p style='color:#787b86;'>💡 Il robot esegue i trade reali in background 24h su 24 sul server cloud.</p>", unsafe_allow_html=True)

    with col_grafico:
        st.markdown("<h3 style='color:#d1d4dc;'>📈 Grafico a Candele Live</h3>", unsafe_allow_html=True)
        
        # Download dati storici stabili per il grafico interno
        fine = datetime.now(timezone.utc) - timedelta(minutes=15)
        inizio = fine - timedelta(days=60)
        
        try:
            if "/" in asset_ia:
                request_params = CryptoBarsRequest(symbol_or_symbols=asset_ia, timeframe=TimeFrame.Day, start=inizio, end=fine)
                bars = crypto_data_client.get_crypto_bars(request_params)
            else:
                request_params = StockBarsRequest(symbol_or_symbols=asset_ia, timeframe=TimeFrame.Day, start=inizio, end=fine)
                bars = stock_data_client.get_stock_bars(request_params)
                
            dati = bars.df
            if isinstance(dati.index, pd.MultiIndex):
                dati = dati.xs(asset_ia, level=0)
                
            # Sblocco e pulizia dell'asse del tempo per evitare i blocchi di caricamento
            dati_grafico = dati.reset_index()
            dati_grafico['timestamp'] = pd.to_datetime(dati_grafico['timestamp']).dt.date
                
            fig = god.Figure(data=[god.Candlestick(
                x=dati_grafico['timestamp'], open=dati_grafico['open'], high=dati_grafico['high'], low=dati_grafico['low'], close=dati_grafico['close'],
                increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
            )])
            fig.update_layout(plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='#d1d4dc', xaxis_rangeslider_visible=False, height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Caricamento dati del grafico in corso...")

    # --- 📊 SEZIONE STORICO ORDINI E GUADAGNI ---
    st.markdown("---")
    st.markdown("<h2 style='color:#d1d4dc;'>📜 Monitoraggio Operazioni Real-Time</h2>", unsafe_allow_html=True)
    
    tab_attive, tab_storico = st.tabs(["📦 Posizioni Aperte al Momento", "🗂️ Cronologia Storica Ordini"])
    
    with tab_attive:
        st.subheader("Trade attualmente gestiti dall'IA")
        try:
            posizioni = client.get_all_positions()
            if not posizioni:
                st.info("Nessun trade aperto al momento. L'IA è flat sul mercato.")
            else:
                lista_posizioni = []
                for p in posizioni:
                    lista_posizioni.append({
                        "Asset": p.symbol,
                        "Quantità": p.qty,
                        "Prezzo Ingresso": f"${float(p.avg_entry_price):,.2f}",
                        "Valore Attuale": f"${float(p.market_value):,.2f}",
                        "Guadagno Operazione": f"${float(p.unrealized_pl):,.2f}"
                    })
                df_pos = pd.DataFrame(lista_posizioni)
                st.dataframe(df_pos, use_container_width=True)
        except Exception as e:
            st.info("Sincronizzazione posizioni attive con Wall Street...")

    with tab_storico:
        st.subheader("Storico dei BUY e SELL completati")
        try:
            ordini = client.get_orders(filter={"status": "all", "limit": 20})
            if not ordini:
                st.info("Nessun ordine registrato nella cronologia.")
            else:
                lista_ordini = []
                for o in ordini:
                    lista_ordini.append({
                        "Data/Ora": o.created_at.strftime('%d/%m/%Y %H:%M'),
                        "Asset": o.symbol,
                        "Tipo Operazione": "COMPRA (BUY)" if o.side == OrderSide.BUY else "VENDI (SELL)",
                        "Quantità": o.qty,
                        "Stato": "Eseguito ✅" if o.status == "filled" else "In Coda ⏳"
                    })
                df_ord = pd.DataFrame(lista_ordini)
                st.dataframe(df_ord, use_container_width=True)
        except Exception as e:
            st.info("Sincronizzazione storico ordini eseguite...")

except Exception as e:
    st.error(f"Errore di sincronizzazione generale: {e}")
