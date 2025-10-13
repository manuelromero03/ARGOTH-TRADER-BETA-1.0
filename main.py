# main.py
import time
from trading_interface import TradingInterface, MT5_AVAILABLE

# ===========================
# 🔹 CONFIGURACIÓN INICIAL
# ===========================
MODE = "real"          # "sim" o "real"
SYMBOL = "EURUSD"
CAPITAL = 1000         # Capital total disponible
RISK_PER_TRADE = 0.01  # 1% del capital por operación
TAKE_PROFIT = 0.005    # 0.5% objetivo de beneficio
STOP_LOSS = 0.003      # 0.3% riesgo máximo
TIMEFRAME_MIN = 1      # Temporalidad (en minutos)
LOOP_INTERVAL = TIMEFRAME_MIN * 60  # segundos

# Inicializar la interfaz de trading
trader = TradingInterface(
    mode=MODE,
    symbol=SYMBOL,
    capital=CAPITAL,
    risk_per_trade=RISK_PER_TRADE
)

print(f"\n💻 Modo: {'MT5 REAL/DEMO' if MODE == 'real' and MT5_AVAILABLE else 'SIMULADOR'}")
print(f"🕒 Comenzando trading automático: {SYMBOL} | Intervalo: {TIMEFRAME_MIN} min\n")

# ===========================
# 🔁 LOOP PRINCIPAL
# ===========================
try:
    while True:
        try:
            # 1️⃣ Obtener datos
            data = trader.get_prices()

            # 2️⃣ Calcular indicadores
            data = trader.calculate_indicators(data)

            # 3️⃣ Generar señal
            signal = trader.generate_signal(data)

            # 4️⃣ Ejecutar trade si hay señal
            if signal:
                trader.execute_trade(
                    signal,
                    take_profit=TAKE_PROFIT,
                    stop_loss=STOP_LOSS
                )

            # 5️⃣ Registrar trade
            trader.log_trade(signal, data)

        except Exception as e:
            print(f"⚠️ Error en el ciclo: {e}")
            time.sleep(10)  # esperar antes de reintentar

        # 6️⃣ Esperar siguiente vela
        print(f"⏳ Esperando {TIMEFRAME_MIN} minuto(s)...\n")
        time.sleep(LOOP_INTERVAL)

except KeyboardInterrupt:
    print("🛑 Trading detenido manualmente por el usuario.")
except Exception as e:
    print(f"❌ Error crítico: {e}")