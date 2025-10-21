# auto_commit.py
import os
import subprocess
import datetime
from pathlib import Path

LOG_PATH = Path("logs/auto_commit.log")

def log_event(message):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
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

        log_event(f"✅ {commit_message} enviado correctamente.")
        print("✅ Auto commit completado y enviado a GitHub.")

    except subprocess.CalledProcessError as e:
        log_event(f"❌ Error en auto commit: {e}")
        print("⚠️ Error al ejecutar auto commit. Revisa logs/auto_commit.log")

def manual_commit(message="Manual commit desde ARGOTH"):
    """Permite un commit manual con mensaje personalizado."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        log_event(f"✅ Commit manual enviado: {message}")
        print("✅ Commit manual completado y enviado.")
    except subprocess.CalledProcessError as e:
        log_event(f"❌ Error en commit manual: {e}")
        print("⚠️ Error en commit manual.")

if __name__ == "__main__":
    auto_commit()