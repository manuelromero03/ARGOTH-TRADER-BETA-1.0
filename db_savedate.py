import csv
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Directorios base para datos y logs
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

# --- Sistema de "Pulso de vida" (ultimo commit registrado) ---

DB_PATH = Path("data") / "argoth_system.db"

def save_last_commit_timestamp():
    """Guarda en la base de datos la fecha, hora y rama de ultimo commit exitoso."""
    from subprocess import run 

    #Asegura existencia de la base de datos y la tabla 
    conn = sqlite3.connect(DB_PATH)
    cursor =  conn.cursor()
    cursor.executer("""
    CREATE TABLE IF NOT EXISTS system_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT, 
                    branch TEXT,
                    timestamp TEXT
                )
                    """)
            
    #Obtiene la rama actual de git
    try: 
        result = run(["git", "branch", "--show-current"], capture_output=True, text=True)
        branch = result.stdout.strip() or "unknown"
    except Exception:
        branch = "unknown"

    #Inserta el registro 
    cursor.execute("""
        INSERT INTO system_status (event, branch, timestamp)
        VALUES (?, ?, ?)
        """, ("Last Succesfull Commit", branch, _timestamp()))
    conn.commit()
    conn.close()
    
    #También lo deja reflejado en los logs del sistema 
    save_system_event("PULSE", f"🧩Commit existoso registrado en rama {'branch'}.")

def get_last_commit_status():
    """Verifica el ultimo commit existoso devuelve en resume del estado."""
    file_path = DATA_DIR /  "last_commit.json"
    if not file_path.exists():
        return "⚠ No se ha registrado ningun commit exitoso aun."
    
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = f.read().strip() 
        timestamp = data.split('"')[3] #Extrae la fecha del JSON simple 
        commit_time = datetime.strip.time(timestamp, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - commit_time 

        minutos = int(delta.total_seconds() // 60)
        if minutos < 1: 
            return f"Utltimo commit exitoso hace unos segundos. ({timestamp}) - ARTGOTH sincronizado."
        elif minutos < 60: 
            return f"Ultimo commit exitoso hace {minutos} min - sistema estable."
        else: 
            horas = minutos // 60 
            return f"⚠ Ultimo commit hace {horas} h - posible inactividad detectada."
        
    except Exception as e:
        save_system_event("ERROR", f"No se pudo leer last_commit.json: {e}")
        return "❌ Error al leer el estado del ultimo commit."




    