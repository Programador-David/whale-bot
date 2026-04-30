import requests
import time
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
LIMITE_BTC = 0.5

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"})

ordens_vistas = set()

def monitorar_bybit(categoria, label):
    try:
        url = "https://api.bybit.com/v5/market/recent-trade"
        params = {"category": categoria, "symbol": "BTCUSDT", "limit": 50}
        r = requests.get(url, params=params, timeout=10)
        dados = r.json()
        trades = dados.get("result", {}).get("list", [])
        if not isinstance(trades, list):
            print(f"{label} resposta inesperada: {dados}")
            return
        for trade in trades:
            if not isinstance(trade, dict):
                continue
            tid = str(trade.get("execId", "")) + "_" + categoria
            qty = float(trade.get("size", 0))
            price = float(trade.get("price", 0))
            side = "🟢 COMPRA" if trade.get("side") == "Buy" else "🔴 VENDA"
            if tid and tid not in ordens_vistas and qty >= LIMITE_BTC:
                ordens_vistas.add(tid)
                valor_usd = qty * price
                msg = (
                    f"<b>{label} — Grande Ordem BTC</b>\n"
                    f"Tipo: {side}\n"
                    f"Quantidade: {qty:.4f} BTC\n"
                    f"Preço: ${price:,.2f}\n"
                    f"Volume: ${valor_usd:,.2f} USDT\n"
                    f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
                enviar_telegram(msg)
                print(f"Alerta enviado: {qty:.4f} BTC {side}")
        print(f"{label} — OK, {len(trades)} trades verificados")
    except Exception as e:
        print(f"Erro {label}: {e}")

print("Bot iniciado — monitorando Bybit Spot + Futuros acima de 0.5 BTC...")
while True:
    monitorar_bybit("spot", "🏦 BYBIT SPOT")
    monitorar_bybit("linear", "📈 BYBIT FUTUROS")
    time.sleep(30)
