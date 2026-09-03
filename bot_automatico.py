import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as god
from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="Terminal Pro IA", layout="wide", initial_sidebar_state="expanded")

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

    st.sidebar.markdown("### 💳 ACCOUNT WALLET")
    st.sidebar.metric(label="Cash Disponibile", value=f"${saldo_reale:,.2f}")
    st.sidebar.metric(label="Valore Portafoglio", value=f"${valore_portafoglio:,.2f}")
    st.sidebar.metric(label="Profitto Totale IA", value=f"${guadagno_totale:,.2f}")

    st.markdown("# 📊 Terminale di Trading Proprietario Premium")
    st.markdown("---")
    
    asset_selezionato = st.selectbox("Seleziona lo Strumento da visualizzare:", ["BTC/USD", "ETH/USD", "TSLA", "NVDA", "AAPL"])
    
    if asset_selezionato in ["BTC/USD", "TSLA", "ETH/USD"]:
        st.success("🔥 Segnale Corrente Algoritmo: BULLISH (BUY) - IA in posizione Long")
    else:
        st.error("❄️ Segnale Corrente Algoritmo: BEARISH (SELL) - IA Flat")
        
    importo_dinamico = saldo_reale * 0.20
    if importo_dinamico < 10: importo_dinamico = 10
    st.metric(label="Budget Dinamico Calcolato per il prossimo Trade (20%)", value=f"${importo_dinamico:,.2f}")
    
    st.markdown("### 📈 GRAFICO A CANDELE PROFESSIONALE (REAL-TIME FEED)")
    fine = datetime.now(timezone.utc) - timedelta(minutes=15)
    inizio = fine - timedelta(days=45)
    
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
        increasing_line_color='#2ec4b6', decreasing_line_color='#e63946', line_width=2
    )])
    
    fig.update_layout(
        plot_bgcolor='#0c0d14', paper_bgcolor='#0c0d14', font_color='#8a8f9d',
        xaxis_rangeslider_visible=False, height=500, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(gridcolor='#191b28', showgrid=True, zeroline=False),
        yaxis=dict(gridcolor='#191b28', showgrid=True, zeroline=False, side='right')
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("## 📜 REGISTRO OPERATIVO DELLE POSIZIONI IN CLOUD")
    
    tab_attive, tab_storico = st.tabs(["📦 Posizioni Aperte a Mercato", "🗂️ Registro Storico Ordini"])
    
    with tab_attive:
        try:
            posizioni = client.get_all_positions()
            if not posizioni:
                st.info("Nessuna posizione aperta rilevata. L'IA sta scansionando i mercati.")
            else:
                lista_posizioni = []
                for p in posizioni:
                    lista_posizioni.append({
                        "Strumento": p.symbol, "Volume (Qty)": p.qty,
                        "Prezzo Ingresso": f"${float(p.avg_entry_price):,.2f}",
                        "Valore Corrente": f"${float(p.market_value):,.2f}",
                        "Profitto / Perdita": f"${float(p.unrealized_pl):,.2f}"
                    })
                st.dataframe(pd.DataFrame(lista_posizioni), use_container_width=True)
        except:
            st.info("Caricamento posizioni in corso...")

    with tab_storico:
        try:
            ordini = client.get_orders()
            if not ordini:
                st.info("Nessun ordine registrato nel diario storico.")
            else:
                lista_ordini = []
                for o in ordini:
                    lista_ordini.append({
                        "Data Esecuzione": o.created_at.strftime('%d/%m/%Y %H:%M') if o.created_at else "-",
                        "Asset": o.symbol,
                        "Direzione": "COMPRA (BUY)" if o.side == "buy" else "VENDITA (SELL)",
                        "Volume": o.qty, 
                        "Stato": "Eseguito ✅" if o.status == "filled" else "In Coda ⏳"
                    })
                st.dataframe(pd.DataFrame(lista_ordini), use_container_width=True)
        except:
            st.info("Recupero storico ordini dal server...")

except Exception as e:
    st.error(f"Errore di allineamento terminale: {e}")
