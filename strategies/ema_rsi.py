import pandas as pd
import numpy as np

# ============================
# 📊 Estrategia EMA50/EMA200 + RSI14
# ============================

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula los indicadores técnicos (EMA y RSI).
    """
    data["EMA50"] = data["close"].ewm(span=50, adjust=False).mean()
    data["EMA200"] = data["close"].ewm(span=200, adjust=False).mean()

    # RSI
    delta = data["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    return data.dropna()


def generate_signal(data: pd.DataFrame) -> dict:
    """
    Genera señal BUY / SELL / HOLD según cruces EMA y RSI.
    """
    if len(data) < 200:
        return {"type": "HOLD", "reason": "Datos insuficientes"}

    last = data.iloc[-1]

    if last["EMA50"] > last["EMA200"] and last["RSI"] > 55:
        return {"type": "BUY", "price": last["close"], "reason": "Tendencia alcista confirmada"}
    elif last["EMA50"] < last["EMA200"] and last["RSI"] < 45:
        return {"type": "SELL", "price": last["close"], "reason": "Tendencia bajista confirmada"}
    else:
        return {"type": "HOLD", "price": last["close"], "reason": "Sin confirmación"}
