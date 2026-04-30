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

def monitorar_binance_spot():
    try:
        url = "https://api.binance.com/api/v3/trades"
        params = {"symbol": "BTCUSDT", "limit": 50}
        r = requests.get(url, params=params, timeout=10)
        trades = r.json()
        if not isinstance(trades, list):
            print(f"Binance Spot resposta inesperada: {trades}")
            return
        for trade in trades:
            if not isinstance(trade, dict):
                continue
            tid = str(trade.get("id", ""))
            qty = float(trade.get("qty", 0))
            price = float(trade.get("price", 0))
            side = "🟢 COMPRA" if not trade.get("isBuyerMaker") else "🔴 VENDA"
            if tid and tid not in ordens_vistas and qty >= LIMITE_BTC:
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
        print(f"Erro Binance Spot: {e}")

def monitorar_bybit_futuros():
    try:
        url = "https://api.bybit.com/v5/market/recent-trade"
        params = {"category": "linear", "symbol": "BTCUSDT", "limit": 50}
        r = requests.get(url, params=params, timeout=10)
        dados = r.json()
        trades = dados.get("result", {}).get("list", [])
        if not isinstance(trades, list):
            print(f"Bybit resposta inesperada: {dados}")
            return
        for trade in trades:
            if not isinstance(trade, dict):
                continue
            tid = str(trade.get("execId", "")) + "_bybit"
            qty = float(trade.get("size", 0))
            price = float(trade.get("price", 0))
            side = "🟢 COMPRA" if trade.get("side") == "Buy" else "🔴 VENDA"
            if tid and tid not in ordens_vistas and qty >= LIMITE_BTC:
                ordens_vistas.add(tid)
                valor_usd = qty * price
                msg = (
                    f"<b>📈 BYBIT FUTUROS — Grande Ordem BTC</b>\n"
                    f"Tipo: {side}\n"
                    f"Quantidade: {qty:.4f} BTC\n"
                    f"Preço: ${price:,.2f}\n"
                    f"Volume: ${valor_usd:,.2f} USDT\n"
                    f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
                enviar_telegram(msg)
                print(msg)
    except Exception as e:
        print(f"Erro Bybit Futuros: {e}")

print("Bot iniciado — monitorando Binance Spot + Bybit Futuros acima de 0.5 BTC...")
while True:
    monitorar_binance_spot()
    monitorar_bybit_futuros()
    time.sleep(30)
