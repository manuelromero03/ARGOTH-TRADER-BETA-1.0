import pandas as pd
import numpy as np
from datetime import datetime

# ====================================================
# 🔹 Generar datos simulados OHLC
# ====================================================
def get_sim_data(symbol="EURUSD", bars=500):
    """
    Genera datos simulados OHLC para un símbolo dado.
    Compatible con TradingInterface.
    """
    now = datetime.now()
    dates = pd.date_range(end=now, periods=bars, freq='min')  # 1 minuto por barra

    # Simulación de precios base con pequeñas variaciones aleatorias
    base = np.linspace(1.05, 1.10, bars) + np.random.normal(0, 0.001, bars)
    open_prices = base
    close_prices = base + np.random.normal(0, 0.0005, bars)
    high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(0, 0.0003, bars)
    low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(0, 0.0003, bars)
    volumes = np.random.randint(100, 1000, bars)

    # Crear DataFrame compatible con trading_interface
    data = pd.DataFrame({
        "Datetime": dates,
        "Open": open_prices,
        "High": high_prices,
        "Low": low_prices,
        "Close": close_prices,
        "Volume": volumes
    })

    return data


# ====================================================
# 🔹 Obtener datos históricos simulados
# ====================================================
def get_historical_data(symbol="EURUSD", timeframe="M1", bars=500):
    """
    Emula la obtención de datos históricos simulados.
    Devuelve DataFrame OHLC con estructura estándar.
    """
    return get_sim_data(symbol, bars)


# ====================================================
# 🔹 Obtener último precio
# ====================================================
def get_latest_price(data):
    """
    Devuelve el último precio de cierre del DataFrame.
    """
    try:
        return float(data["Close"].iloc[-1])
    except Exception as e:
        print(f"⚠️ Error obteniendo último precio: {e}")
        return None


# ====================================================
# 🔹 Snapshot de precios actual (simulado)
# ====================================================
def get_price_snapshot(symbol="EURUSD"):
    """
    Retorna un snapshot de precios actualizados (simulado).
    """
    data = get_sim_data(symbol, bars=10)
    return {
        "symbol": symbol,
        "bid": float(data["Close"].iloc[-1] - 0.0001),
        "ask": float(data["Close"].iloc[-1] + 0.0001),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# ====================================================
# 🔹 Simular ejecución de trade
# ====================================================
def place_trade(symbol, trade_type, price, lot_size, take_profit, stop_loss):
    """
    Simula la ejecución de una operación (sin conexión real).
    """
    print(f"💼 Simulando {trade_type} en {symbol} @ {price:.5f} | Lote: {lot_size:.4f}")
    print(f"🎯 TP: {take_profit*100:.2f}% | 🛑 SL: {stop_loss*100:.2f}%")
