from trading_interface import get_current_price, calculate_indicators, place_trade, get_historical_data, MT5_AVAILABLE
import pandas as pd

def main():
    # Obtener datos históricos
    data = get_historical_data()

    # Calcular indicadores
    data = calculate_indicators(data)

    # Tomar la última fila
    last_row = data.iloc[-1]
    price = last_row["Close"]
    ema50 = last_row["EMA50"]
    ema200 = last_row["EMA200"]
    rsi14 = last_row["RSI14"]

    print(f"Modo: {'MT5' if MT5_AVAILABLE else 'SIMULADOR'}")
    print(f"Precio actual: {price}")
    print(f"EMA50: {ema50}, EMA200: {ema200}, RSI14: {rsi14}")

    # Estrategia simple: EMA50 cruza EMA200
    trade_type = "COMPRA" if ema50 > ema200 else "VENTA"
    place_trade("BTCUSDT", trade_type, price)
    print(f"✅ Trade guardado: BTCUSDT - {trade_type} @ {price}")

if __name__ == "__main__":
    main()
