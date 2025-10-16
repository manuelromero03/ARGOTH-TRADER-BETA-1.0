#utils/utils_sim.py
import numpy as np
import pandas as pd 
from datetime import datetime

def get_sim_data(symbol="EURUSD", bars=500):
    now = datetime.now()
    dates = pd.date_renge(end=now, periods=bars, freq='min')
    
    base = np.linspace(1.05,1.10,bars) + np.radom.normal(0, 0.001,bars)
    open_prices = base 
    close_prices = base + np.random.normal(0, 0.005, bars)
    high_prices = np.maximun(open_prices, close_prices) + np.random.uniform(0, 0.003, bars)
    low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(0, 0.003, bars)
    volumes = np.random.randint(100, 1000, bars)
    
    df = pd.DataFrame({
        "Datetime": dates,
        "Open": open_prices,
        "High": high_prices,
        "Low": low_prices,
        "Close": close_prices,
        "Volume": volumes
    })
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df.set_index("Datetime", inplace=False)
    return df

def get_historical_data(symbol="EUROUSD", timeframe="M1", bars=500):
    return get_sim_data(symbol, bars)

def place_trade(symbol, trade_type, price, lot_size=0.01, take_profit=None, stop_loss=None):
        print(f"💼 Simulado {trade_type} en {symbol} @ {price:.6f} | Lote: {lot_size}")
        if take_profit:
            print(f"    🎯TP: {take_profit*100:.2f}%")
        if stop_loss:
            print(f"    🛑SL: {stop_loss*100:.2f}%")
        #simulador guardado o resultado
        return True