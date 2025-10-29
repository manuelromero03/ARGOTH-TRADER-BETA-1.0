# utils/utils_mt5.py
import pandas as pd
try:
    import MetaTrader5 as mt5
except Exception as e:
    raise ImportError("MetaTrader5 no disponible en este entorno.") from e
from connect_mt5 import connect_mt5

def get_historical_data(cfg, symbol="EURUSD", timeframe=mt5.TIMEFRAME_M1, bars=500):
    """Obtiene datos históricos desde MT5 usando la configuración pasada"""
    if not connect_mt5(cfg):
        return pd.DataFrame()
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    mt5.shutdown()
    
    if rates is None:
        return pd.DataFrame()
    
    df = pd.DataFrame(rates)
    df = df.rename(columns={"time": "Datetime", "open": "Open", "high": "High", 
                            "low": "Low", "close": "Close", "tick_volume": "Volume"})
    df["Datetime"] = pd.to_datetime(df["Datetime"], unit="s")
    return df

def place_trade(cfg, symbol, trade_type, price, volume=0.01, take_profit=None, stop_loss=None):
    """Envía trade a MT5 usando la configuración pasada"""
    if not connect_mt5(cfg):
        print("❌ No se pudo inicializar MT5")
        return False

    if trade_type.upper() in ["BUY", "COMPRA"]:
        order_type = mt5.ORDER_TYPE_BUY
        tp = price * (1 + take_profit) if take_profit else None
        sl = price * (1 - stop_loss) if stop_loss else None
    else:
        order_type = mt5.ORDER_TYPE_SELL
        tp = price * (1 - take_profit) if take_profit else None
        sl = price * (1 + stop_loss) if stop_loss else None

    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 123456,
        "comment": "ARGOTH",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    if tp:
        req["tp"] = tp
    if sl:
        req["sl"] = sl

    res = mt5.order_send(req)
    mt5.shutdown()
    if res.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Error MT5 retcode: {res.retcode}")
        return False
    print(f"💹 Trade enviado a MT5: {trade_type} {symbol} @ {price} (vol {volume})")
    return True

def get_account_balance(cfg):
    """Retorna el balance actual de la cuenta MT5 usando la configuración"""
    if not connect_mt5(cfg):
        return None

    account_info = mt5.account_info()
    mt5.shutdown()

    if account_info is None:
        print("❌ No se pudo obtener info de cuenta")
        return None

    return float(account_info.balance)