# utils_sim.py
import pandas as pd
import numpy as np
import datetime

def get_historical_data(symbol="BTCUSDT", bars=500, timeframe="1m"):
    """
    Devuelve datos históricos simulados para testing.
    """
    now = datetime.datetime.now()
    dates = pd.date_range(end=now, periods=bars, freq='T')  # 'T' = minutos
    prices = np.cumsum(np.random.randn(bars)) + 50000  # precio inicial 50k

    df = pd.DataFrame({
        "time": dates,
        "Open": prices + np.random.randn(bars),
        "High": prices + np.random.rand(bars)*10,
        "Low": prices - np.random.rand(bars)*10,
        "Close": prices,
        "Volume": np.random.randint(1, 10, size=bars)
    })

    return df

def place_trade(symbol, trade_type, price, volume=0.01):
    """
    Simula la ejecución de un trade
    """
    print(f"💹 [SIMULADOR] Trade ejecutado: {trade_type} {symbol} @ {price}")
    return True