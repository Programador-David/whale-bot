import requests
import time
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
BLOCKCHAIR_KEY = os.environ.get("BLOCKCHAIR_KEY")
LIMITE_BTC = 100  # alerta para movimentações acima de 100 BTC

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mensagem})

def buscar_whales():
    url = "https://api.blockchair.com/bitcoin/transactions"
    params = {
        "s": "output_total(desc)",
        "limit": 10,
        "key": BLOCKCHAIR_KEY
    }
    r = requests.get(url, params=params)
    dados = r.json()
    return dados.get("data", [])

transacoes_vistas = set()

def monitorar():
    print("Bot iniciado — monitorando whales BTC...")
    while True:
        try:
            transacoes = buscar_whales()
            for tx in transacoes:
                txid = tx.get("hash")
                btc = tx.get("output_total", 0) / 100_000_000
                if txid not in transacoes_vistas and btc >= LIMITE_BTC:
                    transacoes_vistas.add(txid)
                    msg = (
                        f"🐋 WHALE ALERT — Bitcoin\n"
                        f"Valor: {btc:,.2f} BTC\n"
                        f"TX: https://blockchair.com/bitcoin/transaction/{txid}"
                    )
                    enviar_telegram(msg)
                    print(msg)
        except Exception as e:
            print(f"Erro: {e}")
        time.sleep(60)

if __name__ == "__main__":
    monitorar()
