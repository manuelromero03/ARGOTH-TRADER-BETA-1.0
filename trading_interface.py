import pandas as pd
import numpy as np
import time
import datetime

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

import utils_sim
import utils_mt5


class TradingInterface:
    def __init__(self, mode="sim"):
        """
        Inicializa la interfaz de trading.
        mode: "sim" para simulador o "real" para MetaTrader5
        """
        self.mode = mode
        self.symbol = "EURUSD"
        self.trades_log = "trades_log.csv"

    # ====================================================
    # 🔹 OBTENER PRECIOS
    # ====================================================
    def get_prices(self, symbol=None):
        symbol = symbol or self.symbol

        if self.mode == "real" and MT5_AVAILABLE and mt5.initialize():
            # Datos reales desde MetaTrader5
            data = utils_mt5.get_historical_data(symbol)
        else:
            # Datos simulados desde archivo o generador
            data = utils_sim.get_historical_data(symbol)

        return data

    # ====================================================
    # 🔹 GENERAR SEÑAL
    # ====================================================
    def generate_signal(self, data: pd.DataFrame):
        """
        Genera una señal basada en el cruce de medias móviles y RSI.
        """
        if len(data) < 200:
            return None

        ema50 = data["Close"].ewm(span=50, adjust=False).mean()
        ema200 = data["Close"].ewm(span=200, adjust=False).mean()

        # RSI
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        last_ema50 = ema50.iloc[-1]
        last_ema200 = ema200.iloc[-1]
        last_rsi = rsi.iloc[-1]
        last_price = data["Close"].iloc[-1]

        print(f"\n📊 Precio: {last_price:.5f}")
        print(f"EMA50: {last_ema50:.5f} | EMA200: {last_ema200:.5f} | RSI: {last_rsi:.2f}")

        if last_ema50 > last_ema200 and last_rsi > 55:
            return {"type": "BUY", "price": last_price}
        elif last_ema50 < last_ema200 and last_rsi < 45:
            return {"type": "SELL", "price": last_price}
        else:
            return None

    # ====================================================
    # 🔹 EJECUTAR TRADE
    # ====================================================
    def execute_trade(self, signal):
        """
        Ejecuta el trade dependiendo del modo activo.
        """
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

    # ====================================================
    # 🔹 GUARDAR EN DIARIO
    # ====================================================
    def log_trade(self, signal, data):
        """
        Registra el trade y los indicadores en el diario de trading.
        """
        last_row = data.iloc[-1]
        log_entry = {
            "datetime": datetime.datetime.now(),
            "symbol": self.symbol,
            "price": last_row["Close"],
            "ema50": last_row["Close"].ewm(span=50, adjust=False).mean().iloc[-1],
            "ema200": last_row["Close"].ewm(span=200, adjust=False).mean().iloc[-1],
            "rsi": self._calculate_rsi(data).iloc[-1],
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

    # ====================================================
    # 🔹 RSI AUXILIAR
    # ====================================================
    def _calculate_rsi(self, data, window=14):
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))