#utils/helpers.py
import threading, sys, time 

_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with _lock:
        print(*args, **kwargs)
        sys.stdout.flush()
        
def check_mt5():
    try:
        import MetaTrader5 as mt5
        return True
    except ImportError:
        return False
    