# auto_commit.py
import os
import subprocess
import datetime
from pathlib import Path
from db_savedate import save_last_commit_timestamp
from db_savedate import save_last_commit_timestamp, get_last_commit_status

LOG_PATH = Path("logs/auto_commit.log")

def log_event(message):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def auto_commit():
    """Realiza commits automáticos si hay cambios no guardados."""
    try:
        # Verificar si hay cambios pendientes
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            log_event("No hay cambios pendientes. Nada que commitear.")
            return
        
        # Agregar todos los cambios
        subprocess.run(["git", "add", "."], check=True)

        # Crear mensaje de commit con fecha
        commit_message = f"Auto commit ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Subir cambios
        subprocess.run(["git", "push", "origin", "main"], check=True)
        # Registrar en logs y mostrar pulso del sistema 
        save_last_commit_timestamp() #Registrar la fecha del ultimo commit
        status_message = get_last_commit_status() 
        log_event(f"✅ {commit_message} enviado correctamente. {status_message}")
        print("✅ Auto commit completado y enviado a GitHub./n{status_message}")

    except subprocess.CalledProcessError as e:
        log_event(f"❌ Error en auto commit: {e}")
        print("⚠️ Error al ejecutar auto commit. Revisa logs/auto_commit.log")

def manual_commit(message="Manual commit desde ARGOTH"):
    """Permite un commit manual con mensaje personalizado."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        save_last_commit_timestamp()
        status_message = get_last_commit_status() 
        log_event(f"✅ Commit manual enviado: {message}. {status_message}")
        print("✅ Commit manual completado y enviado./n{status_message}")
    except subprocess.CalledProcessError as e:
        log_event(f"❌ Error en commit manual: {e}")
        print("⚠️ Error en commit manual.")

if __name__ == "__main__":
    auto_commit()