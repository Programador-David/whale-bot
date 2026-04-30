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

def monitorar_spot():
    try:
        url = "https://api.binance.com/api/v3/trades"
        params = {"symbol": "BTCUSDT", "limit": 50}
        r = requests.get(url, params=params, timeout=10)
        trades = r.json()
        for trade in trades:
            tid = str(trade.get("id"))
            qty = float(trade.get("qty", 0))
            price = float(trade.get("price", 0))
            side = "🟢 COMPRA" if not trade.get("isBuyerMaker") else "🔴 VENDA"
            if tid not in ordens_vistas and qty >= LIMITE_BTC:
                ordens_vistas.add(tid)
                valor_usd = qty * price
                msg = (
                    f"<b>🏦 BINANCE SPOT — Grande Ordem BTC</b>\n"
                    f"Tipo: {side}\n"
                    f"Quantidade: {qty:.4f} BTC\n"
                    f"Preço: ${price:,.2f}\n"
                    f"Volume: ${valor_usd:,.2f} USDT\n"
                    f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
                enviar_telegram(msg)
                print(msg)
    except Exception as e:
        print(f"Erro spot: {e}")

def monitorar_futuros():
    try:
        url = "https://fapi.binance.com/fapi/v1/trades"
        params = {"symbol": "BTCUSDT", "limit": 50}
        r = requests.get(url, params=params, timeout=10)
        trades = r.json()
        for trade in trades:
            tid = str(trade.get("id")) + "_fut"
            qty = float(trade.get("qty", 0))
            price = float(trade.get("price", 0))
            side = "🟢 COMPRA" if not trade.get("isBuyerMaker") else "🔴 VENDA"
            if tid not in ordens_vistas and qty >= LIMITE_BTC:
                ordens_vistas.add(tid)
                valor_usd = qty * price
                msg = (
                    f"<b>📈 BINANCE FUTUROS — Grande Ordem BTC</b>\n"
                    f"Tipo: {side}\n"
                    f"Quantidade: {qty:.4f} BTC\n"
                    f"Preço: ${price:,.2f}\n"
                    f"Volume: ${valor_usd:,.2f} USDT\n"
                    f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
                enviar_telegram(msg)
                print(msg)
    except Exception as e:
        print(f"Erro futuros: {e}")

print("Bot Binance iniciado — monitorando ordens BTC acima de 0.5 BTC...")
while True:
    monitorar_spot()
    monitorar_futuros()
    time.sleep(30)
