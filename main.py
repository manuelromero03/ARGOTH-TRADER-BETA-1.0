## ================================================
# 🤖 ARGOTH v2.5 - Núcleo Central de Ejecución
# ================================================
import time
import platform
import pandas as pd
import numpy as np
from datetime import datetime
import traceback

# ================================================
# 📦 Imports internos
# ================================================
from trading_interface import TradingInterface
from config import SYMBOL, CAPITAL, RISK_PER_TRADE, INTERVAL_TYPE, INTERVAL_VALUE, MT5_CREDENTIALS
from utils.utils_ibkr import save_trade_to_db

# ================================================
# 🧰 Generador de datos simulados (modo seguro)
# ================================================
def get_sim_data(symbol="EURUSD", bars=500):
    """
    Genera datos simulados de precios OHLC para pruebas del sistema.
    """
    now = datetime.now()
    dates = pd.date_range(end=now, periods=bars, freq='min')

    base = np.linspace(1.05, 1.10, bars) + np.random.normal(0, 0.001, bars)
    open_prices = base
    close_prices = base + np.random.normal(0, 0.0005, bars)
    high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(0, 0.0003, bars)
    low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(0, 0.0003, bars)

    data = pd.DataFrame({
        "time": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": np.random.randint(100, 1000, bars)
    })
    data["time"] = pd.to_datetime(data["time"])
    data.set_index("time", inplace=True)
    return data

# ================================================
# 🧩 Intentar importar MetaTrader5
# ================================================
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 no disponible en este sistema.\n🎮 Modo simulador activado.\n")

# ================================================
# 🔐 Detectar conexión MT5
# ================================================
def detect_mt5_connection(credentials):
    if not MT5_AVAILABLE:
        return False

    try:
        mt5.shutdown()
        if mt5.initialize(
            login=credentials["login"],
            password=credentials["password"],
            server=credentials["server"]
        ):
            account_info = mt5.account_info()
            if account_info:
                print(f"✅ Conectado a MT5 | {account_info.name} | Saldo: {account_info.balance:.2f}")
                return True
        print("⚠️ No se pudo conectar a MT5. Cambiando a simulación.\n")
        mt5.shutdown()
        return False
    except Exception as e:
        print(f"❌ Error al conectar con MT5: {e}")
        return False

# ================================================
# 🧭 Configuración inicial automática
# ================================================
MODE = "real" if detect_mt5_connection(MT5_CREDENTIALS) else "sim"

if INTERVAL_TYPE == "seconds":
    LOOP_INTERVAL = INTERVAL_VALUE
elif INTERVAL_TYPE == "minutes":
    LOOP_INTERVAL = INTERVAL_VALUE * 60
elif INTERVAL_TYPE == "hours":
    LOOP_INTERVAL = INTERVAL_VALUE * 3600
else:
    LOOP_INTERVAL = 60  # fallback

# ================================================
# 🚀 Inicializar interfaz de trading
# ================================================
trader = TradingInterface(
    mode=MODE,
    symbol=SYMBOL,
    capital=CAPITAL,
    risk_per_trade=RISK_PER_TRADE
)

print(f"\n{'='*55}")
print(f"🤖 ARGOTH-TRADE v2.5 — Sistema Autónomo Multi-OS")
print(f"💻 Sistema: {platform.system()}")
print(f"💾 Modo actual: {'MT5 (Real)' if MODE == 'real' else 'SIMULADOR'}")
print(f"📈 Símbolo: {SYMBOL}")
print(f"⏱️ Intervalo: {INTERVAL_VALUE} {INTERVAL_TYPE}")
print(f"{'='*55}\n")

# ================================================
# 🔁 Ciclo de ejecución principal
# ================================================
def run_cycle(trader):
    """
    Ejecuta un ciclo completo de análisis, decisión y ejecución.
    """
    try:
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🕒 Iniciando ciclo: {start_time}")

        data = trader.get_prices()
        data = trader.calculate_indicators(data)
        signal = trader.generate_signal(data)
        trader.execute_trade(signal)
        trader.log_trade(signal, data)
        save_trade_to_db(signal, data)

        print(f"✅ Ciclo completado ({signal}) — {datetime.now().strftime('%H:%M:%S')}\n")

    except Exception as e:
        print(f"❌ Error en ciclo: {e}")
        traceback.print_exc()
        print("⏳ Reintentando en 10 segundos...\n")
        time.sleep(10)

# ================================================
# 🧠 Control interactivo del sistema
# ================================================
running = True
paused = False

try:
    while running:
        command = input("Comando (run/pause/resume/status/stop): ").strip().lower()

        if command == "run":
            print("\n🚀 Iniciando ciclo automático...\n")
            while not paused and running:
                run_cycle(trader)
                print(f"⏳ Esperando {INTERVAL_VALUE} {INTERVAL_TYPE}...\n")
                time.sleep(LOOP_INTERVAL)

        elif command == "pause":
            paused = True
            print("⏸️ Ciclo pausado.\n")

        elif command == "resume":
            paused = False
            print("▶️ Reanudando ejecución...\n")

        elif command == "status":
            estado = "Pausado" if paused else "Activo"
            print(f"📊 Estado: {estado} | Modo: {MODE.upper()} | Símbolo: {SYMBOL}\n")

        elif command == "stop":
            running = False
            print("🛑 ARGOTH detenido manualmente.\n")

        else:
            print("⚠️ Comando no reconocido. Usa: run, pause, resume, status, stop\n")

except KeyboardInterrupt:
    print("\n🛑 Trading detenido manualmente (Ctrl+C).")
finally:
    if MT5_AVAILABLE:
        mt5.shutdown()
    print("🔚 Sistema cerrado correctamente.\n")
