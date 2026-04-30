import requests
import time
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
LIMITE_BTC = 100

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mensagem})

transacoes_vistas = set()

def monitorar():
    print("Bot iniciado v2 — monitorando whales BTC...")
    while True:
        try:
            url = "https://mempool.space/api/mempool/recent"
            r = requests.get(url, timeout=10)
            dados = r.json()
            print(f"Tipo recebido: {type(dados)} — Total: {len(dados) if isinstance(dados, list) else 'N/A'}")
            if not isinstance(dados, list):
                print(f"Resposta inesperada: {dados}")
                time.sleep(60)
                continue
            for tx in dados:
                txid = tx.get("txid")
                valor = tx.get("value", 0) / 100_000_000
                if txid and txid not in transacoes_vistas and valor >= LIMITE_BTC:
                    transacoes_vistas.add(txid)
                    msg = (
                        f"🐋 WHALE ALERT — Bitcoin\n"
                        f"Valor: {valor:,.2f} BTC\n"
                        f"TX: https://mempool.space/tx/{txid}"
                    )
                    enviar_telegram(msg)
                    print(msg)
        except Exception as e:
            print(f"Erro detalhado: {e}")
        time.sleep(60)

if __name__ == "__main__":
    monitorar()
