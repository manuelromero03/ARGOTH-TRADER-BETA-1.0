# main.py
import time
import platform
from core.trade_manager import TradeManager
from config import CONFIG

def main():
    print(f"\nARGOTH v3.0 — ARRANCANDO (OS: {platform.system()})\n")
    manager = TradeManager(CONFIG)

    # CLI simple
    running = True
    paused = False

    try:
        while running:
            cmd = input("Comando (run/pause/resume/stop/status): ").strip().lower()
            if cmd == "run":
                print("🚀 Iniciando loop automático. Ctrl+C para interrumpir.\n")
                while True:
                    if paused:
                        time.sleep(1)
                        continue
                    manager.run_cycle()
                    # intervalo según config
                    interval_type = CONFIG["interval_type"]
                    v = CONFIG["interval_value"]
                    if interval_type == "seconds":
                        sleep_t = v
                    elif interval_type == "minutes":
                        sleep_t = v * 60
                    elif interval_type == "hours":
                        sleep_t = v * 3600
                    else:
                        sleep_t = 60
                    print(f"⏳ Esperando {v} {interval_type}...\n")
                    time.sleep(sleep_t)

            elif cmd == "pause":
                paused = True
                print("⏸️  Pausado.\n")
            elif cmd == "resume":
                paused = False
                print("▶️  Reanudado.\n")
            elif cmd == "status":
                print(f"📊 Estado: {'Pausado' if paused else 'Activo'} | Modo: {manager.mode}\n")
            elif cmd == "stop":
                running = False
                print("🛑 Detenido por usuario.\n")
            else:
                print("Comando no reconocido. Usa: run, pause, resume, status, stop\n")

    except KeyboardInterrupt:
        print("\n🛑 Stop por teclado.")
    finally:
        manager.shutdown()
        print("🔚 ARGOTH cerrado correctamente.")

if __name__ == "__main__":
    main()
