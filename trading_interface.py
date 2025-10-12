# trading_interface.py
import pandas as pd
import numpy as np
import datetime
import platform
import sys

# ====================================================
# 🔹 Detección de MetaTrader5
# ====================================================
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# ====================================================
# 🔹 Cargar módulos auxiliares
# ====================================================
try:
    import utils_sim
except ImportError:
    print("⚠️ No se encontró utils_sim.py.")
    sys.exit(1)

try:
    import utils_mt5
except ImportError:
    utils_mt5 = None  # opcional si no se usa modo real

# ====================================================
# 🔹 Clase principal de Trading
# ====================================================
class TradingInterface:
    def __init__(self, mode="sim", symbol="EURUSD", trades_log="trades_log.csv",
                 capital=1000, risk_per_trade=0.01, take_profit=0.01, stop_loss=0.01):
        """
        Inicializa la interfaz de trading.
        """
        self.mode = mode.lower()
        self.symbol = symbol
        self.trades_log = trades_log
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.take_profit = take_profit
        self.stop_loss = stop_loss

        print(f"🚀 Iniciando TradingInterface en modo [{self.mode.upper()}] para {self.symbol}")
        print(f"🖥️ Sistema operativo detectado: {platform.system()}")

        if self.mode == "real" and MT5_AVAILABLE:
            if not mt5.initialize():
                raise RuntimeError("❌ No se pudo inicializar MetaTrader5.")
            else:
                info = mt5.account_info()
                print(f"✅ Conectado a MT5: {self.symbol} | Servidor: {info.server} | Saldo: {info.balance}")
        else:
            print("🧪 Modo simulador activado (sin conexión a MT5).")

    # ====================================================
    # 🔹 Obtener precios históricos
    # ====================================================
    def get_prices(self):
        if self.mode == "real" and MT5_AVAILABLE:
            data = utils_mt5.get_historical_data(self.symbol)
            # Normalizar columnas
            if 'close' in data.columns:
                data = data.rename(columns={
                    'time': 'Datetime',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'tick_volume': 'Volume'
                })
        else:
            data = utils_sim.get_historical_data(self.symbol)

        if data is None or len(data) == 0:
            raise ValueError(f"⚠️ No se pudieron obtener datos para {self.symbol}")

        # Convertir datetime y establecer índice
        data['Datetime'] = pd.to_datetime(data['Datetime'])
        data.set_index('Datetime', inplace=True)
        return data

    # ====================================================
    # 🔹 Calcular indicadores técnicos
    # ====================================================
    def calculate_indicators(self, data: pd.DataFrame):
        data["EMA50"] = data["Close"].ewm(span=50, adjust=False).mean()
        data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()
        data["RSI14"] = self._calculate_rsi(data)
        return data

    # ====================================================
    # 🔹 Generar señal de compra/venta
    # ====================================================
    def generate_signal(self, data: pd.DataFrame):
        if len(data) < 200:
            print("⚠️ Datos insuficientes para generar señal.")
            return None

        last = data.iloc[-1]
        print(f"\n📊 {self.symbol} | Precio: {last['Close']:.5f}")
        print(f"EMA50: {last['EMA50']:.5f} | EMA200: {last['EMA200']:.5f} | RSI: {last['RSI14']:.2f}")

        if last["EMA50"] > last["EMA200"] and last["RSI14"] > 55:
            return {"type": "BUY", "price": last["Close"]}
        elif last["EMA50"] < last["EMA200"] and last["RSI14"] < 45:
            return {"type": "SELL", "price": last["Close"]}
        else:
            return None

    # ====================================================
    # 🔹 Ejecutar trade (simulado o real)
    # ====================================================
    def execute_trade(self, signal):
        if not signal:
            print("⏸️ No hay señal para ejecutar.")
            return

        trade_type = signal["type"]
        price = signal["price"]

        # Calcular tamaño de lote basado en riesgo
        lot_size = self.capital * self.risk_per_trade / price

        if self.mode == "real" and MT5_AVAILABLE:
            print(f"💹 Ejecutando trade real: {trade_type} @ {price} | Lote: {lot_size:.4f}")
            utils_mt5.place_trade(self.symbol, trade_type, price, lot_size,
                                  take_profit=self.take_profit, stop_loss=self.stop_loss)
        else:
            print(f"🧪 Ejecutando trade simulado: {trade_type} @ {price} | Lote: {lot_size:.4f}")
            utils_sim.place_trade(self.symbol, trade_type, price, lot_size,
                                  take_profit=self.take_profit, stop_loss=self.stop_loss)

    # ====================================================
    # 🔹 Registrar trade en el diario
    # ====================================================
    def log_trade(self, signal, data):
        last = data.iloc[-1]
        log_entry = {
            "datetime": last.name,
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

    # ====================================================
    # 🔹 Función auxiliar RSI
    # ====================================================
    def _calculate_rsi(self, data, window=14):
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
