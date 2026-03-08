from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os
import json
from threading import Thread

app = Flask(__name__)

# ===== CONFIGURAÇÕES =====
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

session = HTTP(
    testnet=False,  # True se usar testnet
    api_key=API_KEY,
    api_secret=API_SECRET,
)

@app.route("/")
def home():
    return "Bot Bybit rodando 🚀"


# ===== FUNÇÃO QUE EXECUTA O TRADE =====
def executar_ordem(symbol, side, qty, sl, tp1, tp2, tp3):

    try:

        print("Executando trade...")

        # Ordem principal
        session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=qty,
        )

        # Stop Loss
        session.set_trading_stop(
            category="linear",
            symbol=symbol,
            stopLoss=str(sl),
        )

        # Take Profit 1
        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            orderType="Limit",
            qty=qty * 0.33,
            price=str(tp1),
            reduceOnly=True,
        )

        # Take Profit 2
        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            orderType="Limit",
            qty=qty * 0.33,
            price=str(tp2),
            reduceOnly=True,
        )

        # Take Profit 3
        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            orderType="Limit",
            qty=qty * 0.34,
            price=str(tp3),
            reduceOnly=True,
        )

        print("Trade executado com sucesso")

    except Exception as e:
        print("Erro ao executar trade:", e)


# ===== WEBHOOK DO TRADINGVIEW =====
@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.get_data(as_text=True)
        data = json.loads(data)

        symbol = data.get("symbol")
        side = data.get("side")
        qty = float(data.get("qty"))
        sl = float(data.get("sl"))
        tp1 = float(data.get("tp1"))
        tp2 = float(data.get("tp2"))
        tp3 = float(data.get("tp3"))

        print("Webhook recebido:", data)

        # Executa trade em segundo plano (evita timeout)
        Thread(
            target=executar_ordem,
            args=(symbol, side, qty, sl, tp1, tp2, tp3)
        ).start()

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
