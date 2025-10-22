import csv
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
LOG_DIR = Path("logs")

# Asegura directorios base
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _timestamp():
    """Devuelve el timestamp estándar del sistema ARGOTH."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _write_csv(file_path, headers, data_row):
    """Manejo unificado de escritura en CSV con manejo de errores."""
    try:
        exists = file_path.exists()
        with file_path.open(mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(headers)
            writer.writerow(data_row)
    except Exception as e:
        save_system_event("ERROR", f"Falló escritura en {file_path.name}: {e}")

def save_trade(symbol, action, price, volume, profit=0.0, comment=""):
    """Guarda los trades ejecutados (manuales o automáticos)."""
    file_path = DATA_DIR / "trades_log.csv"
    _write_csv(file_path, 
        ["timestamp", "symbol", "action", "price", "volume", "profit", "comment"],
        [_timestamp(), symbol, action, price, volume, profit, comment]
    )

def save_signal(symbol, signal_type, ema_fast, ema_slow, rsi, comment=""):
    """Guarda las señales generadas por las estrategias."""
    file_path = DATA_DIR / "signals_log.csv"
    _write_csv(file_path,
        ["timestamp", "symbol", "signal", "ema_fast", "ema_slow", "rsi", "comment"],
        [_timestamp(), symbol, signal_type, ema_fast, ema_slow, rsi, comment]
    )

def save_price(symbol, price):
    """Guarda los precios monitoreados."""
    file_path = DATA_DIR / "precios.csv"
    _write_csv(file_path,
        ["timestamp", "symbol", "price"],
        [_timestamp(), symbol, price]
    )

def save_system_event(event_type, detail):
    """Registra eventos del sistema ARGOTH (errores, pausas, commits, etc.)."""
    file_path = LOG_DIR / "system_events.log"
    try:
        with file_path.open(mode="a", encoding="utf-8") as f:
            f.write(f"[{_timestamp()}] {event_type}: {detail}\n")
    except Exception as e:
        print(f"[CRITICAL] Error registrando evento del sistema: {e}")

def save_last_commit():
    """Registra la fecha del último commit exitoso."""
    file_path = DATA_DIR / "last_commit.json"
    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(f'{{"last_commit": "{_timestamp()}"}}')
        save_system_event("PULSE", "🧩 ARGOTH actualizado correctamente (commit exitoso).")
    except Exception as e:
        save_system_event("ERROR", f"No se pudo guardar last_commit.json: {e}")