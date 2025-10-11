import pandas as pd
import numpy as np
import datetime

# =======================
# 🔹 Detección MT5
# =======================
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

import utils_sim
import utils_mt5

# =======================
# 🔹 Clase principal
# =======================
class TradingInterface:
    def __init__(self, mode="sim", symbol="EURUSD", trades_log="trades_log.csv"):
        """
        Inicializa la interfaz de trading.
        mode: "sim" para simulador o "real" para MT5
        """
        self.mode = mode
        self.symbol = symbol
        self.trades_log = trades_log

    # =======================
    # 🔹 Obtener precios
    # =======================
    def get_prices(self):
        if self.mode == "real" and MT5_AVAILABLE and mt5.initialize():
            data = utils_mt5.get_historical_data(self.symbol)
        else:
            data = utils_sim.get_historical_data(self.symbol)
        return data

    # =======================
    # 🔹 Calcular indicadores
    # =======================
    def calculate_indicators(self, data: pd.DataFrame):
        data["EMA50"] = data["Close"].ewm(span=50, adjust=False).mean()
        data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()
        data["RSI14"] = self._calculate_rsi(data)
        return data

    # =======================
    # 🔹 Generar señal
    # =======================
    def generate_signal(self, data: pd.DataFrame):
        if len(data) < 200:
            return None

        last = data.iloc[-1]
        print(f"\n📊 Precio: {last['Close']:.5f}")
        print(f"EMA50: {last['EMA50']:.5f} | EMA200: {last['EMA200']:.5f} | RSI: {last['RSI14']:.2f}")

        if last["EMA50"] > last["EMA200"] and last["RSI14"] > 55:
            return {"type": "BUY", "price": last["Close"]}
        elif last["EMA50"] < last["EMA200"] and last["RSI14"] < 45:
            return {"type": "SELL", "price": last["Close"]}
        else:
            return None

    # =======================
    # 🔹 Ejecutar trade
    # =======================
    def execute_trade(self, signal):
        if not signal:
            return
        trade_type = signal["type"]
        price = signal["price"]

        if self.mode == "real" and MT5_AVAILABLE:
            print(f"💹 Ejecutando trade real: {trade_type} @ {price}")
            utils_mt5.place_trade(self.symbol, trade_type, price)
        else:
            print(f"🧪 Ejecutando trade simulado: {trade_type} @ {price}")
            utils_sim.place_trade(self.symbol, trade_type, price)

    # =======================
    # 🔹 Guardar en diario
    # =======================
    def log_trade(self, signal, data):
        last = data.iloc[-1]
        log_entry = {
            "datetime": datetime.datetime.now(),
            "symbol": self.symbol,
            "price": last["Close"],
            "ema50": last["EMA50"],
            "ema200": last["EMA200"],
            "rsi": last["RSI14"],
            "signal": signal["type"] if signal else "NONE",
            "mode": self.mode,
        }

        df = pd.DataFrame([log_entry])
        try:
            old_df = pd.read_csv(self.trades_log)
            df = pd.concat([old_df, df], ignore_index=True)
        except FileNotFoundError:
            pass

        df.to_csv(self.trades_log, index=False)
        print(f"📝 Trade registrado ({self.mode.upper()}) - {signal['type'] if signal else 'NONE'}")

    # =======================
    # 🔹 Función auxiliar RSI
    # =======================
    def _calculate_rsi(self, data, window=14):
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
