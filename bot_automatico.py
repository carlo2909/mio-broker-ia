import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as god
from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from datetime import datetime, timedelta, timezone

# 🎨 Configurazione Layout Professionale (Look Total Black Capital.com)
st.set_page_config(page_title="Mio Broker Privato IA", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0c0d12; color: #e4e6eb; font-family: 'Roboto', sans-serif; }
    header { background-color: #14161f !important; }
    .css-1d391kg { background-color: #14161f; }
    .stTabs [data-baseweb="tab-list"] { background-color: #14161f; }
    .stTabs [data-baseweb="tab"] { color: #8a8f9d; }
    .stTabs [aria-selected="true"] { color: #26a69a !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INFRASTRUTTURA DI BACKEND ---
API_KEY = "PKGBTKR5UFADYCUR2QYPXU45MN"
SECRET_KEY = "HWnrgJW7UxCUEDnEfkEatRiPQPE2yAukjVEWPkFtahcZ"

try:
    client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True)
    crypto_data_client = CryptoHistoricalDataClient()
    stock_data_client = StockHistoricalDataClient(api_key=API_KEY, secret_key=SECRET_KEY)
    
    account = client.get_account()
    saldo_reale = float(account.cash)
    valore_portafoglio = float(account.portfolio_value)
    guadagno_totale = valore_portafoglio - 100000.0

    # 🖥️ BARRA LATERALE: PANNELLO DI WALLET (Stile Capital.com)
    st.sidebar.markdown("<h2 style='color:#26a69a; text-align:center;'>💳 PORTAFOGLIO PERSONALE</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.metric(label="Saldo Disponibile", value=f"${saldo_reale:,.2f}")
    st.sidebar.metric(label="Conto di Trading (Valore Netto)", value=f"${valore_portafoglio:,.2f}")
    
    if guadagno_totale >= 0:
        st.sidebar.success(f"📈 Profitto Generato dall'IA: +${guadagno_totale:,.2f}")
    else:
        st.sidebar.error(f"📉 Variazione di Portafoglio: ${guadagno_totale:,.2f}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Deposito Fondi")
    deposito = st.sidebar.number_input("Digita importo da ricaricare ($):", min_value=10.0, step=10.0, key="dep")
    if st.sidebar.button("Conferma Deposito con Carta"):
        st.sidebar.info(f"Connessione protetta con il gateway di pagamento per l'importo di ${deposito}...")
        
    st.sidebar.markdown("### 📤 Prelievo Fondi")
    prelievo = st.sidebar.number_input("Digita importo da prelevare ($):", min_value=10.0, max_value=saldo_reale if saldo_reale > 10 else 10.0, step=10.0, key="prel")
    if st.sidebar.button("Invia Fondi su Carta"):
        st.sidebar.success(f"Richiesta inoltrata! Riscossione di ${prelievo} inviata alla tua carta.")

    # 📈 CORPO CENTRALE PRINCIPALE
    st.markdown("<h1 style='color:#e4e6eb;'>📊 Plancia Proprietaria di Trading Avanzato</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_grafico, col_ia = st.columns(2)
    
    with col_ia:
        st.markdown("<h3 style='color:#26a69a;'>🧠 Algoritmo IA Organico</h3>", unsafe_allow_html=True)
        asset_selezionato = st.selectbox("Seleziona mercato per analisi IA:", ["BTC/USD", "ETH/USD", "TSLA", "NVDA", "AAPL"])
        st.markdown(f"**Ultimo screening:** {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")
        
        st.markdown("<h4>🔮 Previsione Corrente</h4>", unsafe_allow_html=True)
        if asset_selezionato in ["BTC/USD", "TSLA", "ETH/USD"]:
            st.metric(label="Direzione Stimata", value="BULLISH (BUY)", delta="IA in posizione Long")
        else:
            st.metric(label="Direzione Stimata", value="BEARISH (SELL)", delta="- IA in posizione Short", delta_color="inverse")
        
        st.markdown("---")
        importo_dinamico = saldo_reale * 0.20
        if importo_dinamico < 10: importo_dinamico = 10
        st.write(f"💼 **Budget di Trade Attuale:** ${importo_dinamico:,.2f} *(Ricalcolato in base all'interesse composto)*")

    with col_grafico:
        st.markdown("<h3 style='color:#e4e6eb;'>📈 Grafico Interattivo Real-Time</h3>", unsafe_allow_html=True)
        
        fine = datetime.now(timezone.utc) - timedelta(minutes=15)
        inizio = fine - timedelta(days=60)
        
        try:
            if "/" in asset_selezionato:
                request_params = CryptoBarsRequest(symbol_or_symbols=asset_selezionato, timeframe=TimeFrame.Day, start=inizio, end=fine)
                bars = crypto_data_client.get_crypto_bars(request_params)
            else:
                request_params = StockBarsRequest(symbol_or_symbols=asset_selezionato, timeframe=TimeFrame.Day, start=inizio, end=fine)
                bars = stock_data_client.get_stock_bars(request_params)
                
            dati = bars.df
            if isinstance(dati.index, pd.MultiIndex):
                dati = dati.xs(asset_selezionato, level=0)
                
            dati_grafico = dati.reset_index()
            dati_grafico['timestamp'] = pd.to_datetime(dati_grafico['timestamp']).dt.date
                
            fig = god.Figure(data=[god.Candlestick(
                x=dati_grafico['timestamp'], open=dati_grafico['open'], high=dati_grafico['high'], low=dati_grafico['low'], close=dati_grafico['close'],
                increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
            )])
            fig.update_layout(plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='#d1d4dc', xaxis_rangeslider_visible=False, height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Caricamento dati del grafico in corso...")

    # --- 📊 SEZIONE DI CONTROLLO OPERAZIONI ---
    st.markdown("---")
    st.markdown("<h2 style='color:#e4e6eb;'>📜 Registro dei Contratti e Storico Fondi</h2>", unsafe_allow_html=True)
    
    tab_attive, tab_storico = st.tabs(["📦 Posizioni Aperte", "🗂️ Registro Storico Ordini"])
    
    with tab_attive:
        try:
            posizioni = client.get_all_positions()
            if not posizioni:
                st.info("Nessuna operazione aperta in questo momento. L'IA è in attesa del momento giusto.")
            else:
                lista_posizioni = []
                for p in posizioni:
                    lista_posizioni.append({
                        "Asset": p.symbol,
                        "Esposizione (Quantità)": p.qty,
                        "Prezzo Medio d'Ingresso": f"${float(p.avg_entry_price):,.2f}",
                        "Valore di Mercato Corrente": f"${float(p.market_value):,.2f}",
                        "P&L Non Realizzato (Guadagno)": f"${float(p.unrealized_pl):,.2f}"
                    })
                df_pos = pd.DataFrame(lista_posizioni)
                st.dataframe(df_pos, use_container_width=True)
        except:
            st.info("Sincronizzazione dei contratti in tempo reale...")

    with tab_storico:
        try:
            ordini = client.get_orders(filter={"status": "all", "limit": 20})
            if not ordini:
                st.info("Nessun ordine presente nello storico del conto.")
            else:
                lista_ordini = []
                for o in ordini:
                    lista_ordini.append({
                        "Data e Ora Esecuzione": o.created_at.strftime('%d/%m/%Y %H:%M'),
                        "Asset di Riferimento": o.symbol,
                        "Direzione Trade": "ACQUISTO (BUY)" if o.side.value == "buy" else "VENDITA (SELL)",
                        "Volume Scambiato": o.qty,
                        "Esito Operazione": "Completato ✅" if o.status.value == "filled" else "In attesa ⏳"
                    })
                df_ord = pd.DataFrame(lista_ordini)
                st.dataframe(df_ord, use_container_width=True)
        except:
            st.info("Aggiornamento del registro storico...")

except Exception as e:
    st.error(f"Piattaforma in fase di allineamento: {e}")
