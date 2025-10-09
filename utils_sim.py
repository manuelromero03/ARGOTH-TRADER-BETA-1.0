# utils_sim.py 
# Modulo con funciones para calcular tecnicos (EMA, RSI) 

import pandas as pd 

def calculate_ema(prices, period):
    """
    Calcula la media movil exponecial (EMA)
    """
    series = pd.Series(prices)
    ema = series.ewm(span=period, adjust=False).mean()
    return ema.tolist()

def calculate_rsi(prices, period=14):
    """Calcula el RSI (Relative Strength Index)"""
    series = pd.Series(prices)
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0).tolist()