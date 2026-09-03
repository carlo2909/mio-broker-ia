import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide

st.set_page_config(page_title="TradingView & Alpaca Ecosystem", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #ffffff; color: #131722; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    header { background-color: #ffffff !important; border-bottom: 1px solid #e0e3eb; }
    .alpaca-container { background: #ffffff; padding: 24px; border: 1px solid #e0e3eb; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .alpaca-title { font-size: 18px; font-weight: 600; color: #131722; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
    .sub-txt { font-size: 12px; color: #787b86; font-weight: 400; }
    .stDataFrame table { border-collapse: collapse; width: 100%; }
    .stDataFrame th { background-color: #f8f9fd !important; color: #606266 !important; font-weight: 600 !important; font-size: 13px !important; border-bottom: 1px solid #e0e3eb !important; padding: 12px !important; }
    .stDataFrame td { padding: 12px !important; font-size: 13px !important; border-bottom: 1px solid #f0f3fa !important; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "PKGBTKR5UFADYCUR2QYPXU45MN"
SECRET_KEY = "HWnrgJW7UxCUEDnEfkEatRiPQPE2yAukjVEWPkFtahcZ"

try:
    client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True)
    account = client.get_account()
    saldo_reale = float(account.cash)
    importo_dinamico = saldo_reale * 0.20
    if importo_dinamico < 10: importo_dinamico = 10

    st.markdown("<div style='padding: 10px 20px; background:#f8f9fd; border-bottom:1px solid #e0e3eb; font-size:13px;'>💼 <b>Money Management Attivo:</b> Budget Dinamico Interesse Composto (20%): <b>$" + f"{importo_dinamico:,.2f}" + "</b></div>", unsafe_allow_html=True)

    # --- 📈 PANNELLO AVANZATO ORIGINALE DI TRADINGVIEW SBLOCCATO CON IFRAME NATIVO ---
    tradingview_iframe_url = "https://tradingview.com"
    
    st.markdown(f'<iframe src="{tradingview_iframe_url}" width="100%" height="600" frameborder="0" allowfullscreen="true" scrolling="no" style="border:1px solid #e0e3eb; border-radius:8px;"></iframe>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 🏦 TABELLA TOP POSITIONS STYLE ALPACA ---
    st.markdown("<div class='alpaca-container'>", unsafe_allow_html=True)
    st.markdown("<div class='alpaca-title'>Top Positions <span class='sub-txt'>View All</span></div>", unsafe_allow_html=True)
    try:
        posizioni = client.get_all_positions()
        if not posizioni:
            st.info("Nessuna posizione aperta in portafoglio.")
        else:
            lista_posizioni = []
            for p in posizioni:
                p_l = float(p.unrealized_pl)
                p_l_str = f"+${p_l:,.2f}" if p_l >= 0 else f"-${abs(p_l):,.2f}"
                lista_posizioni.append({
                    "Asset": p.symbol,
                    "Price": f"${float(p.current_price):,.2f}",
                    "Qty": round(float(p.qty), 4),
                    "Market Value": f"${float(p.market_value):,.2f}",
                    "Total P/L ($)": p_l_str
                })
            st.dataframe(pd.DataFrame(lista_posizioni), use_container_width=True, hide_index=True)
    except:
        st.info("Caricamento posizioni attive...")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- 📜 TABELLA RECENT ORDERS STYLE ALPACA ---
    st.markdown("<div class='alpaca-container'>", unsafe_allow_html=True)
    st.markdown("<div class='alpaca-title'>Recent Orders <span class='sub-txt'>View All</span></div>", unsafe_allow_html=True)
    try:
        ordini = client.get_orders(filter={"status": "all", "limit": 10})
        if not ordini:
            st.info("Nessun ordine recente trovato.")
        else:
            lista_ordini = []
            for o in ordini:
                lista_ordini.append({
                    "Asset": o.symbol,
                    "Type": o.type.value.upper() if o.type else "MARKET",
                    "Side": o.side.value.lower(),
                    "Qty": float(o.qty) if o.qty else 0.0,
                    "Filled Qty": float(o.filled_qty) if o.filled_qty else 0.0,
                    "Avg Fill Price": f"${float(o.filled_avg_price):,.2f}" if o.filled_avg_price else "-",
                    "Status": o.status.value.lower(),
                    "Source": "access_key",
                    "Submitted At": o.created_at.strftime('%b %d, %Y, %I:%M:%S %p') if o.created_at else "-"
                })
            st.dataframe(pd.DataFrame(lista_ordini), use_container_width=True, hide_index=True)
    except:
        st.info("Caricamento registro ordini...")
    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Terminale in fase di allineamento grafico: {e}")
