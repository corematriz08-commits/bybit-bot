from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os

app = Flask(__name__)

# ===== CONFIGURAÇÕES =====
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

session = HTTP(
    testnet=False,  # coloque True se for usar testnet
    api_key=API_KEY,
    api_secret=API_SECRET,
)

@app.route("/")
def home():
    return "Bot Bybit rodando 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    symbol = data.get("symbol")
    side = data.get("side")  # Buy ou Sell
    qty = float(data.get("qty"))
    sl = float(data.get("sl"))
    tp1 = float(data.get("tp1"))
    tp2 = float(data.get("tp2"))
    tp3 = float(data.get("tp3"))

    try:
        # Ordem principal
        order = session.place_order(
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

        # Take Profits (parciais)
        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            orderType="Limit",
            qty=qty * 0.33,
            price=str(tp1),
            reduceOnly=True,
        )

        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            orderType="Limit",
            qty=qty * 0.33,
            price=str(tp2),
            reduceOnly=True,
        )

        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            orderType="Limit",
            qty=qty * 0.34,
            price=str(tp3),
            reduceOnly=True,
        )

        return jsonify({"status": "Ordem enviada com sucesso"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
