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
        print(f"{label} status: {r.status_code}")
        print(f"{label} resposta bruta: {r.text[:300]}")
        dados = r.json()
        retcode = dados.get("retCode", -1)
        if retcode != 0:
            print(f"{label} erro retCode: {dados.get('retMsg')}")
            return
        trades = dados.get("result", {}).get("list", [])
        count = 0
        for trade in trades:
            if not isinstance(trade, dict):
                continue
            tid = str(trade.get("execId") or trade.get("i", "")) + "_" + categoria
            qty = float(trade.get("size") or trade.get("v") or 0)
            price = float(trade.get("price") or trade.get("p") or 0)
            side_raw = trade.get("side") or trade.get("S", "")
            side = "🟢 COMPRA" if side_raw == "Buy" else "🔴 VENDA"
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
                count += 1
        print(f"{label} — {len(trades)} trades, {count} alertas")
    except Exception as e:
        print(f"Erro {label}: {e}")

print("Bot iniciado — monitorando Bybit Spot + Futuros acima de 0.5 BTC...")
while True:
    monitorar_bybit("spot", "🏦 BYBIT SPOT")
    monitorar_bybit("linear", "📈 BYBIT FUTUROS")
    time.sleep(60)
