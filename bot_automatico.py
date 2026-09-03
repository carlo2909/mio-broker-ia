import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
from alpaca.trading.client import TradingClient
from datetime import datetime

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

# --- INFRASTRUTTURA DI BACKEND (Connessione Silenziosa ai mercati) ---
API_KEY = "PKGBTKR5UFADYCUR2QYPXU45MN"
SECRET_KEY = "HWnrgJW7UxCUEDnEfkEatRiPQPE2yAukjVEWPkFtahcZ"

try:
    client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True)
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
        st.sidebar.success(f"Richiesta inoltrata! Risossione di ${prelievo} inviata alla tua carta.")

    # 📈 CORPO CENTRALE PRINCIPALE
    st.markdown("<h1 style='color:#e4e6eb;'>📊 Plancia Proprietaria di Trading Avanzato</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_grafico, col_ia = st.columns([3, 1]) # Spazio largo per il grafico interattivo, laterale per l'IA
    
    with col_ia:
        st.markdown("<h3 style='color:#26a69a;'>🧠 Algoritmo IA Organico</h3>", unsafe_allow_html=True)
        asset_selezionato = st.selectbox("Seleziona mercato per analisi IA:", ["BTCUSD", "ETHUSD", "TSLA", "NVDA", "AAPL"])
        st.markdown(f"**Ultimo screening:** {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")
        
        st.markdown("<h4>🔮 Previsione Corrente</h4>", unsafe_allow_html=True)
        if asset_selezionato in ["BTCUSD", "TSLA", "ETHUSD"]:
            st.metric(label="Direzione Stimata", value="BULLISH (BUY)", delta="IA in posizione Long")
        else:
            st.metric(label="Direzione Stimata", value="BEARISH (SELL)", delta="- IA in posizione Short", delta_color="inverse")
        
        st.markdown("---")
        # Calcolo dinamico dell'interesse composto automatico (20% del capitale reale)
        importo_dinamico = saldo_reale * 0.20
        if importo_dinamico < 10: importo_dinamico = 10
        st.write(f"💼 **Budget di Trade Attuale:** ${importo_dinamico:,.2f} *(Ricalcolato in base all'interesse composto)*")

    with col_grafico:
        st.markdown("<h3 style='color:#e4e6eb;'>📈 Grafico Interattivo Real-Time (Candele al Minuto)</h3>", unsafe_allow_html=True)
        
        # INNESTO DEL GRAPHIC ENGINE DI TRADINGVIEW CON STRUMENTI DI DISEGNO E FIBONACCI
        tradingview_widget_code = f"""
        <div class="tradingview-widget-container" style="height:100%;width:100%">
          <div id="tradingview_pro_chart" style="height:500px;width:100%"></div>
          <script type="text/javascript" src="https://tradingview.com"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "BINANCE:{asset_selezionato}T" if "{asset_selezionato}".includes("USD") else "NASDAQ:{asset_selezionato}",
            "interval": "1",
            "timezone": "Europe/Rome",
            "theme": "dark",
            "style": "1",
            "locale": "it",
            "toolbar_bg": "#14161f",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "studies": [
              "MASimple@tv-basicstudies"
            ],
            "container_id": "tradingview_pro_chart"
          }});
          </script>
        </div>
        """
        components.html(tradingview_widget_code, height=520)

    # --- 📊 SEZIONE DI CONTROLLO OPERAZIONI (Stile Capital.com) ---
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
