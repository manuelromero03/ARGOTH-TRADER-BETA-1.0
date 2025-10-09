# main.py
# Código base para ARGOTH - inicio de tu bot de trading

# Importar funciones de utilidades (que crearemos después)
from utils_mt5 import get_price_mt5
from utils_sim import calculate_ema, calculate_rsi
from utils_ibkr import save_trade_to_db

def main():
    symbol = "BTCUSDT"  # Puedes cambiar al activo que quieras
    # Obtener precios
    prices = get_price_mt5(symbol, n=200)  # Últimos 200 precios

    # Calcular indicadores
    ema50 = calculate_ema(prices, 50)
    ema200 = calculate_ema(prices, 200)
    rsi14 = calculate_rsi(prices, 14)

    # Mostrar información
    print(f"Precio actual: {prices[-1]}")
    print(f"EMA50: {ema50[-1]}, EMA200: {ema200[-1]}, RSI14: {rsi14[-1]}")

    # Guardar trade de ejemplo
    save_trade_to_db(symbol, "COMPRA", prices[-1])

if __name__ == "__main__":
    main()
