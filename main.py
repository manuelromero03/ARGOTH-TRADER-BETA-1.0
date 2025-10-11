import os
import time
import importlib
import pandas as pd

# Intentamos importar MetaTrader5, si no está disponible usaremos el simulador
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# Importamos los módulos internos
import utils_sim
import utils_mt5
from trading_interface import TradingInterface


def initialize_trading_system():
    """
    Inicializa el sistema de trading, elige modo automático (simulación o real),
    y devuelve una instancia de TradingInterface configurada.
    """
    if MT5_AVAILABLE:
        print("✅ MetaTrader5 detectado. Intentando conexión...")
        if mt5.initialize():
            print("🟢 Modo REAL activado (MT5 conectado).")
            return TradingInterface(mode="real")
        else:
            print("⚠️ MT5 detectado, pero no se pudo conectar. Iniciando simulador...")
            return TradingInterface(mode="sim")
    else:
        print("🧩 MetaTrader5 no disponible. Iniciando simulador...")
        return TradingInterface(mode="sim")


def main():
    print("\n🚀 Iniciando sistema ARGOTH Beta\n")

    trading_system = initialize_trading_system()

    print(f"🔁 Modo actual: {trading_system.mode.upper()}")

    while True:
        try:
            # Obtener precios
            prices = trading_system.get_prices(symbol="EURUSD")

            # Procesar señales
            signal = trading_system.generate_signal(prices)

            # Ejecutar operación si aplica
            if signal:
                trading_system.execute_trade(signal)

            # Guardar registro
            trading_system.log_trade(signal, prices)

            # Esperar siguiente ciclo (ej: 1 min)
            time.sleep(60)

        except KeyboardInterrupt:
            print("\n🛑 ARGOTH detenido manualmente.")
            break

        except Exception as e:
            print(f"⚠️ Error en el ciclo principal: {e}")
            time.sleep(5)
            continue


if __name__ == "__main__":
    main()