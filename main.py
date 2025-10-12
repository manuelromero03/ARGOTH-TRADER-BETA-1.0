# main.py
import time
from trading_interface import TradingInterface, MT5_AVAILABLE

# ===========================
# 🔹 Configuración inicial
# ===========================
MODE = "real"  # "sim" o "real"
SYMBOL = "EURUSD"
CAPITAL = 1000
RISK_PER_TRADE = 0.01
TIMEFRAME_MIN = 1
LOOP_INTERVAL = TIMEFRAME_MIN * 60

# Inicializar trader
trader = TradingInterface(mode=MODE, symbol=SYMBOL, capital=CAPITAL, risk_per_trade=RISK_PER_TRADE)

print(f"💻 Modo: {'MT5' if MODE == 'real' and MT5_AVAILABLE else 'SIMULADOR'}")
print(f"🕒 Comenzando trading automático: {SYMBOL} | Intervalo: {TIMEFRAME_MIN} min\n")

# ===========================
# 🔹 Loop principal de trading
# ===========================
try:
    while True:
        # 1️⃣ Obtener datos
        data = trader.get_prices()

        # 2️⃣ Calcular indicadores
        data = trader.calculate_indicators(data)

        # 3️⃣ Generar señal
        signal = trader.generate_signal(data)

        # 4️⃣ Ejecutar trade
        trader.execute_trade(signal)

        # 5️⃣ Guardar en diario
        trader.log_trade(signal, data)

        # 6️⃣ Esperar siguiente ciclo
        print(f"⏳ Esperando {TIMEFRAME_MIN} minuto(s)...\n")
        time.sleep(LOOP_INTERVAL)

except KeyboardInterrupt:
    print("🛑 Trading detenido manualmente.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
