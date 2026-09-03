import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as god
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta, timezone

# 🎨 Configurazione stile TradingView (Scuro e tecnico)
st.set_page_config(page_title="TradingView IA Broker", layout="wide", initial_sidebar_state="expanded")

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

    # 🖥️ BARRA LATERALE: PORTAFOGLIO E WALLET CARTE
    st.sidebar.image("https://wikimedia.org", width=150)
    st.sidebar.markdown("<h2 style='color:#d1d4dc;'>💳 ACCOUNT WALLET</h2>", unsafe_allow_html=True)
    st.sidebar.metric(label="Saldo Netto Prelevabile", value=f"${saldo_reale:,.2f}")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Deposita Fondi")
    deposito = st.sidebar.number_input("Importo da caricare ($):", min_value=10.0, step=50.0, key="dep")
    if st.sidebar.button("Deposita con Carta"):
        st.sidebar.info(f"Reindirizzamento sicuro a Stripe per ${deposito}... (Tariffa 1.4% a carico utente)")
        
    st.sidebar.subheader("📤 Preleva Fondi")
    prelievo = st.sidebar.number_input("Importo da riscuotere ($):", min_value=10.0, max_value=saldo_reale if saldo_reale > 10 else 10.0, step=50.0, key="prel")
    if st.sidebar.button("Invia Fondi alla Carta"):
        st.sidebar.success(f"Richiesta inviata! ${prelievo} in accredito sulla tua carta.")

    # 📈 CORPO PRINCIPALE: INTERFACCIA TRADINGVIEW DI RICERCA
    st.markdown("<h1 style='color:#d1d4dc; font-family:sans-serif;'>📊 Piattaforma TradingView IA Private</h1>", unsafe_allow_html=True)
    
    col_grafico, col_ia = st.columns()
    
    with col_ia:
        st.markdown("<h3 style='color:#d1d4dc;'>🔎 Cerca Mercato</h3>", unsafe_allow_html=True)
        ticker_cercato = st.text_input("Inserisci il codice (es. BTC/USD, TSLA, NVDA, AAPL, AMZN):", value="BTC/USD").upper().strip()
        st.markdown(f"**Ultimo Controllo:** {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")

    # Download Storico Dati Dinamico
    fine = datetime.now(timezone.utc) - timedelta(minutes=15)
    inizio = fine - timedelta(days=365)
    
    if "/" in ticker_cercato:
        request_params = CryptoBarsRequest(symbol_or_symbols=ticker_cercato, timeframe=TimeFrame.Day, start=inizio, end=fine)
        bars = crypto_data_client.get_crypto_bars(request_params)
    else:
        request_params = StockBarsRequest(symbol_or_symbols=ticker_cercato, timeframe=TimeFrame.Day, start=inizio, end=fine)
        bars = stock_data_client.get_stock_bars(request_params)
        
    dati = bars.df
    if isinstance(dati.index, pd.MultiIndex):
        dati = dati.xs(ticker_cercato, level=0)
        
    with col_grafico:
        # Grafico a candele TradingView Style corretto
        fig = god.Figure(data=[god.Candlestick(
            x=dati.index, open=dati['open'], high=dati['high'], low=dati['low'], close=dati['close'],
            increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        )])
        
        fig.update_layout(
            plot_bgcolor='#131722', paper_bgcolor='#131722', modebar_bgcolor='#1c2030',
            font_color='#d1d4dc', xaxis_rangeslider_visible=True, height=600,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<p style='color:#787b86;'>💡 Sposta il mouse per analizzare le candele. Usa la barra di ricerca a destra per cambiare grafico istantaneamente.</p>", unsafe_allow_html=True)

    # --- CALCOLI ED ESECUZIONE IA INTERNA (Random Forest) ---
    dati["Ritorno"] = dati["close"].pct_change()
    dati["Media_Mobile_5"] = dati["close"].rolling(window=5).mean()
    dati["Media_Mobile_20"] = dati["close"].rolling(window=20).mean()
    dati["Target"] = np.where(dati["close"].shift(-1) > dati["close"], 1, 0)
    dati_puliti = dati.dropna().copy()

    X = dati_puliti[["Ritorno", "Media_Mobile_5", "Media_Mobile_20"]]
    y = dati_puliti["Target"]
    X_train = X.iloc[:-1]
    y_train = y.iloc[:-1]
    ultimo_giorno = X.iloc[[-1]]

    modello = RandomForestClassifier(n_estimators=100, random_state=42)
    modello.fit(X_train, y_train)
    previsione = modello.predict(ultimo_giorno)

    # Esecuzione Ordine e Visualizzazione Statistiche
    with col_ia:
        st.markdown("<h4 style='color:#d1d4dc;'>📦 Stato Posizione</h4>", unsafe_allow_html=True)
        try:
            posizione = client.get_open_position(ticker_cercato)
            st.success(f"Trade Attivo! Qty: {posizione.qty}")
        except:
            st.info("Nessun trade aperto su questo asset.")
            
        st.markdown("<h4 style='color:#d1d4dc;'>🔮 Decisione IA</h4>", unsafe_allow_html=True)
        if previsione == 1:
            st.metric(label="Previsione di Mercato", value="BULLISH (BUY)", delta="Segnale di Acquisto")
        else:
            st.metric(label="Previsione di Mercato", value="BEARISH (SELL)", delta="- Segnale di Vendita", delta_color="inverse")

        # Gestione automatica del budget tarata a 10$ per simulare il conto da 50€
        tif = TimeInForce.GTC if "/" in ticker_cercato else TimeInForce.DAY
        try:
            posizione_reale = client.get_open_position(ticker_cercato)
            if previsione == 0:
                ordine = MarketOrderRequest(symbol=ticker_cercato, qty=posizione_reale.qty, side=OrderSide.SELL, time_in_force=tif)
                client.submit_order(order_data=ordine)
        except:
            if previsione == 1:
                prezzo_attuale = float(dati["close"].iloc[-1])
                qty_calcolata = round(10 / prezzo_attuale, 4) if "/" in ticker_cercato else round(10 / prezzo_attuale, 2)
                if qty_calcolata <= 0: qty_calcolata = 1
                ordine = MarketOrderRequest(symbol=ticker_cercato, qty=qty_calcolata, side=OrderSide.BUY, time_in_force=tif)
                client.submit_order(order_data=ordine)

except Exception as e:
    st.error(f"Asset non riconosciuto o errore di sincronizzazione: {e}")
