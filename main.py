# ==============================
# 📘 main.py — ARGOTH v2.3 (Cross-Platform)
# ==============================
import time
import platform
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_sim_data(symbol="EURUSD", bars=500):
    """
    Genera datos simulados de precios OHLC para pruebas.
    """
    now = datetime.now()
    # Cambiamos 'T' (deprecated) por 'min'
    dates = pd.date_range(end=now, periods=bars, freq='min')
    
    # Generar precios base simulados
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
    
    # Aseguramos que 'time' esté en formato datetime
    data["time"] = pd.to_datetime(data["time"])
    data.set_index("time", inplace=True)
    
    return data

def get_latest_price(data):
    """
    Retorna el último precio de cierre simulado.
    """
    try:
        return float(data["close"].iloc[-1])
    except Exception as e:
        print(f"⚠️ Error obteniendo último precio: {e}")
        return None
# Intentar importar MetaTrader5 (solo en Windows)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 no disponible en este sistema(Linux/macOS/Codespaces).\n")
    print("🎮 Modo simulador activado.")
    
from trading_interface import TradingInterface

# ==============================
# 🔹 CONFIGURACIÓN BASE
# ==============================
SYMBOL = "EURUSD"
CAPITAL = 1000
RISK_PER_TRADE = 0.01
INTERVAL_TYPE = "seconds"   # "seconds", "minutes", "hours"
INTERVAL_VALUE = 10

# ==============================
# 🔹 CREDENCIALES MT5 (solo si MT5_AVAILABLE)
# ==============================
MT5_CREDENTIALS = {
    "login": 51234567,                       # tu número de cuenta
    "password": "tu_contraseña_mt5",         # contraseña de MT5
    "server": "ICMarketsSC-Demo"             # o ICMarketsSC-Real
}

# ==============================
# 🔹 DETECTAR CONEXIÓN MT5
# ==============================
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
            if account_info is not None:
                print(f"✅ Conectado a MT5: {account_info.name} | Servidor: {credentials['server']} | Saldo: {account_info.balance}")
                return True
        print("⚠️ No se pudo conectar a MT5. Usando modo simulador.")
        mt5.shutdown()
        return False
    except Exception as e:
        print(f"❌ Error al conectar con MT5: {e}")
        return False

# ==============================
# 🔹 SELECCIÓN AUTOMÁTICA DE MODO
# ==============================
MODE = "real" if detect_mt5_connection(MT5_CREDENTIALS) else "sim"

# ==============================
# 🔹 INTERVALO DE EJECUCIÓN
# ==============================
if INTERVAL_TYPE == "seconds":
    LOOP_INTERVAL = INTERVAL_VALUE
elif INTERVAL_TYPE == "minutes":
    LOOP_INTERVAL = INTERVAL_VALUE * 60
elif INTERVAL_TYPE == "hours":
    LOOP_INTERVAL = INTERVAL_VALUE * 3600
else:
    LOOP_INTERVAL = 60

# ==============================
# 🔹 INICIALIZAR TRADER
# ==============================
trader = TradingInterface(
    mode=MODE,
    symbol=SYMBOL,
    capital=CAPITAL,
    risk_per_trade=RISK_PER_TRADE
)

print(f"\n{'='*55}")
print(f"🤖 ARGOTH-TRADE v2.3 — Sistema Autónomo Multi-OS")
print(f"💻 Sistema: {platform.system()}")
print(f"💾 Modo actual: {'MT5 (ICMarkets)' if MODE == 'real' else 'SIMULADOR'}")
print(f"📈 Símbolo: {SYMBOL}")
print(f"⏱️ Intervalo: {INTERVAL_VALUE} {INTERVAL_TYPE}")
print(f"{'='*55}\n")

# ==============================
# 🔹 LOOP PRINCIPAL CONTROLADO
# ==============================
def run_cycle(trader):
    try:
        data = trader.get_prices()
        data = trader.calculate_indicators(data)
        signal = trader.generate_signal(data)
        trader.execute_trade(signal)
        trader.log_trade(signal, data)
        print("✅ Ciclo completado.\n")
    except Exception as e:
        print(f"❌ Error en ciclo: {e}\n")

running = True
paused = False

try:
    while running:
        command = input("Comando (run/pause/resume/stop/status): ").strip().lower()

        if command == "run":
            print("🚀 Iniciando ciclo automático...\n")
            while not paused:
                run_cycle(trader)
                print(f"⏳ Esperando {INTERVAL_VALUE} {INTERVAL_TYPE}...\n")
                time.sleep(LOOP_INTERVAL)

        elif command == "pause":
            paused = True
            print("⏸️  Ciclo pausado.\n")

        elif command == "resume":
            paused = False
            print("▶️  Reanudando...\n")

        elif command == "status":
            print(f"📊 Estado: {'Pausado' if paused else 'Activo'} | Modo: {MODE}\n")

        elif command == "stop":
            running = False
            print("🛑 ARGOTH detenido manualmente.\n")

        else:
            print("⚠️ Comando no reconocido. Usa: run, pause, resume, status, stop\n")

except KeyboardInterrupt:
    print("\n🛑 Trading detenido por teclado.")
finally:
    if MT5_AVAILABLE:
        mt5.shutdown()
    print("🔚 Sistema cerrado correctamente.")
