import csv
import os
from datetime import datetime

DATA_DIR = "data"

# Asegura que exista el directorio
os.makedirs(DATA_DIR, exist_ok=True)

def save_trade(symbol, action, price, volume, profit=0.0, comment=""):
    """Guarda los trades ejecutados (manuales o automáticos)."""
    file_path = os.path.join(DATA_DIR, "trades_log.csv")
    exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "symbol", "action", "price", "volume", "profit", "comment"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            action,
            price,
            volume,
            profit,
            comment
        ])

def save_signal(symbol, signal_type, ema_fast, ema_slow, rsi, comment=""):
    """Guarda las señales generadas por las estrategias."""
    file_path = os.path.join(DATA_DIR, "signals_log.csv")
    exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "symbol", "signal", "ema_fast", "ema_slow", "rsi", "comment"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            signal_type,
            ema_fast,
            ema_slow,
            rsi,
            comment
        ])

def save_price(symbol, price):
    """Guarda los precios monitoreados."""
    file_path = os.path.join(DATA_DIR, "precios.csv")
    exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "symbol", "price"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            price
        ])

def save_system_event(event_type, detail):
    """Guarda eventos del sistema ARGOTH (errores, pausas, etc.)."""
    file_path = os.path.join("logs", "system_events.log")
    os.makedirs("logs", exist_ok=True)

    with open(file_path, mode="a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event_type}: {detail}\n")
