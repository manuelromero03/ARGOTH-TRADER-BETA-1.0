#utils/helpers.py
import threading, sys, time 

_lock = threading.lock()

def safe_print(*args, **kwargs):
    with _lock:
        print(*args, **kwargs)
        sys.stdout.flush()
            