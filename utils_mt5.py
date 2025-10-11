# utils_mt5.py
import pandas as pd
import MetaTrader5 as mt5

def get_historical_data(symbol="EURUSD", timeframe=mt5.TIMEFRAME_M1, bars=500):
    """
    Obtiene datos históricos desde MetaTrader5
    """
    if not mt5.initialize():
        print("❌ No se pudo inicializar MT5")
        return pd.DataFrame()

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    mt5.shutdown()

    if rates is None:
        return pd.DataFrame()

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def place_trade(symbol, trade_type, price, volume=0.01):
    """
    Ejecuta un trade en MT5
    """
    if not mt5.initialize():
        print("❌ No se pudo inicializar MT5")
        return False

    if trade_type.upper() in ["COMPRA", "BUY"]:
        order_type = mt5.ORDER_TYPE_BUY
    elif trade_type.upper() in ["VENTA", "SELL"]:
        order_type = mt5.ORDER_TYPE_SELL
    else:
        print("❌ Tipo de trade inválido")
        return False

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 123456,
        "comment": "ARGOTH Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    mt5.shutdown()

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Error al ejecutar trade: {result.retcode}")
        return False

    print(f"💹 Trade ejecutado en MT5: {trade_type} {symbol} @ {price}")
    return True
