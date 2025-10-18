import pandas as pd
import numpy as np

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    print("⚠️ MetaTrader5 no disponible. Usando modo simulador.")
    mt5 = None
    MT5_AVAILABLE = False


def get_historical_data(symbol="EURUSD", timeframe=None, bars=500):
    """Obtiene datos de MT5 o genera datos simulados si MT5 no está disponible."""
    if MT5_AVAILABLE and timeframe is not None:
        if not mt5.initialize():
            print("❌ No se pudo inicializar MT5. Cambiando a modo simulador.")
            return simulate_data(bars)
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        mt5.shutdown()
        if rates is None:
            print("⚠️ No se pudieron obtener datos de MT5. Usando datos simulados.")
            return simulate_data(bars)
        df = pd.DataFrame(rates)
        df.rename(columns={
            "time": "Datetime", "open": "Open", "high": "High",
            "low": "Low", "close": "Close", "tick_volume": "Volume"
        }, inplace=True)
        df["Datetime"] = pd.to_datetime(df["Datetime"], unit="s")
        return df
    else:
        return simulate_data(bars)


def simulate_data(bars=500):
    """Genera datos falsos (simulados) para pruebas sin MT5."""
    np.random.seed(42)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=bars, freq="1min")
    prices = np.cumsum(np.random.randn(bars)) + 100
    df = pd.DataFrame({
        "Datetime": dates,
        "Open": prices + np.random.randn(bars),
        "High": prices + np.random.rand(bars),
        "Low": prices - np.random.rand(bars),
        "Close": prices,
        "Volume": np.random.randint(100, 1000, bars)
    })
    return df


def place_trade(symbol, trade_type, price, volume=0.01, take_profit=None, stop_loss=None):
    """Ejecuta una orden en MT5 o imprime simulación."""
    if not MT5_AVAILABLE:
        print(f"💻 Simulación: {trade_type} {symbol} @ {price:.5f} (vol {volume})")
        return True

    if not mt5.initialize():
        print("❌ No se pudo inicializar MT5")
        return False

    trade_type = trade_type.upper()
    if trade_type in ["BUY", "COMPRA"]:
        order_type = mt5.ORDER_TYPE_BUY
        tp = price * (1 + (take_profit or 0))
        sl = price * (1 - (stop_loss or 0))
    else:
        order_type = mt5.ORDER_TYPE_SELL
        tp = price * (1 - (take_profit or 0))
        sl = price * (1 + (stop_loss or 0))

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
        "tp": tp,
        "sl": sl
    }

    res = mt5.order_send(req)
    mt5.shutdown()
    if res.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Error MT5 retcode: {res.retcode}")
        return False

    print(f"💹 Trade ejecutado en MT5: {trade_type} {symbol} @ {price:.5f} (vol {volume})")
    return True