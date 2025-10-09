#trading_interface.py 
try: 
    from utils_mt5 import get_current_price, calculate_indicators, place_trade, get_historial
    MT5_AVAILABLE = True 
    print("📎 conectando a MT5")
except ImportError:
    from utils_sim import get_current_price, calculate_indicators, place_trade, get_historial_data
    MT5_AVAILABLE = False 
    print("⚡ Usando simulador de trading")