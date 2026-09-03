
import numpy as np
import pandas as pd
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timezone

# --- CHIAVI ALPACA (Reinserisci i tuoi codici tra le virgolette) ---
API_KEY = "PKFPGXZO5XJCFFWXJMSKRK5WCV"
SECRET_KEY = "9h2rufjAykyymk9FMz7murhYURMChS5Cr3jcF2WekSHY"

# LISTA DEI GRAFICI FOREX DA ANALIZZARE CONTEMPORANEAMENTE
# Su Yahoo Finance il Forex si scrive "Valuta1Valuta2=X"
COPPIE_FOREX = ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "EURGBP=X"]

# Impostazioni ad alto guadagno/rischio
IMPORTO_PER_TRADE = 20000  # Investe $20.000 virtuali per ogni valuta per spingere al massimo i profitti
LIMITE_GIORNI = 5         # Chiude tutto tassativamente entro 1 settimana

try:
    client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=True)
    print("🚀 === AVVIO BOT IA MULTI-FOREX AD ALTO RENDIMENTO ===")

    # L'IA analizza ogni grafico nella lista uno dopo l'altro
    for simbolo in COPPIE_FOREX:
        print(f"\n📈 Analizzando il grafico di: {simbolo}...")
        
        # Scarica i dati storici del grafico Forex
        dati = yf.download(simbolo, start="2020-01-01", progress=False)
        if dati.empty:
            continue

        # Calcolo indicatori matematici sul grafico
        dati["Ritorno"] = dati["Close"].pct_change()
        dati["Media_Mobile_5"] = dati["Close"].rolling(window=5).mean()
        dati["Media_Mobile_20"] = dati["Close"].rolling(window=20).mean()
        dati["Target"] = np.where(dati["Close"].shift(-1) > dati["Close"], 1, 0)
        dati_puliti = dati.dropna().copy()

        X = dati_puliti[["Ritorno", "Media_Mobile_5", "Media_Mobile_20"]]
        y = dati_puliti["Target"]

        X_train = X.iloc[:-1]
        y_train = y.iloc[:-1]
        ultimo_giorno = X.iloc[[-1]]

        # L'IA studia i pattern di questo specifico grafico
        modello = RandomForestClassifier(n_estimators=100, random_state=42)
        modello.fit(X_train, y_train)
        previsione = modello.predict(ultimo_giorno)

        # Traduciamo il simbolo di Yahoo in quello di Alpaca (es. EURUSD=X diventa EUR/USD)
        simbolo_alpaca = simbolo.replace("=X", "")
        if "JPY" not in simbolo_alpaca:
            simbolo_alpaca = f"{simbolo_alpaca[:3]}/{simbolo_alpaca[3:]}"
        else:
            simbolo_alpaca = f"{simbolo_alpaca[:3]}/{simbolo_alpaca[3:]}"

        # Controllo portafoglio su Alpaca
        posizione_attiva = False
        forza_vendita_temporale = False
        
        try:
            # Nota: Alpaca richiede un formato pulito per il forex, saltiamo il controllo se la coppia non è abilitata sul tuo tier
            posizione = client.get_open_position(simbolo_alpaca)
            posizione_attiva = True
            
            giorni_passati = (datetime.now(timezone.utc) - position.create_at).days
            if giorni_passati >= LIMITE_GIORNI:
                forza_vendita_temporale = True
        except Exception:
            pass

        # Decisioni dell'IA applicate al broker
        if forza_vendita_temporale:
            print(f"🔴 TEMPO SCADUTO: Chiudo il trade su {simbolo_alpaca}")
            # Logica di vendita (Alpaca richiede contratti specifici per Forex, inviamo ordine di chiusura)
            try:
                ordine = MarketOrderRequest(symbol=simbolo_alpaca, qty=1, side=OrderSide.SELL, time_in_force=TimeInForce.GTC)
                client.submit_order(order_data=ordine)
            except: pass

        elif previsione == 1:
            print(f"🟢 L'IA prevede RIALZO su {simbolo_alpaca}.")
            if not posizione_attiva:
                print(f"🛒 COMPRA AUTOMATICO: Investo ${IMPORTO_PER_TRADE} su {simbolo_alpaca}")
                # Nota: Calcoliamo la quantità approssimativa in base al budget impostato
                try:
                    prezzo_attuale = float(dati["Close"].iloc[-1])
                    qty_calcolata = round(IMPORTO_PER_TRADE / prezzo_attuale, 2)
                    ordine = MarketOrderRequest(symbol=simbolo_alpaca, qty=qty_calcolata, side=OrderSide.BUY, time_in_force=TimeInForce.GTC)
                    client.submit_order(order_data=ordine)
                    print("✅ Ordine inviato ad Alpaca!")
                except Exception as e:
                    print(f"⚠️ Impossibile inviare ordine (Verifica se il tuo conto demo supporta la leva sul Forex): {e}")
            else:
                print("💡 Trade già aperto sul grafico. Mantengo la posizione.")
                
        elif previsione == 0:
            print(f"🔴 L'IA prevede RIBASSO su {simbolo_alpaca}.")
            if posizione_attiva:
                print(f"💰 VENDI AUTOMATICO: Chiudo il trade su {simbolo_alpaca}")
                try:
                    ordine = MarketOrderRequest(symbol=simbolo_alpaca, qty=1, side=OrderSide.SELL, time_in_force=TimeInForce.GTC)
                    client.submit_order(order_data=ordine)
                    print("✅ Ordine inviato!")
                except: pass
            else:
                print("💡 Grafico debole, nessuna operazione attiva.")

    print("\n=============================================")
    print("📡 Tutti i grafici Forex sono stati scansionati.")
    print("=============================================\n")

except Exception as e:
    print(f"❌ Errore generale del sistema: {e}")

input("Premi Invio per uscire...")
