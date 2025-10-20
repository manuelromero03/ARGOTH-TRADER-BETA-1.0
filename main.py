import time
import platform
import threading
from core.trade_manager import TradeManager
from config import CONFIG

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 no disponible. ARGOTH usará modo SIMULADOR.\n")


def trading_loop(manager, loop_state):
    """Loop de trading que corre en un hilo separado"""
    while loop_state["running"]:
        if loop_state["active"] and not loop_state["paused"]:
            manager.run_cycle()

            # Usa manager.delay si existe, sino usa CONFIG
            sleep_t = getattr(manager, "delay", CONFIG["interval_value"])
            interval_type = CONFIG["interval_type"]

            if interval_type == "seconds":
                sleep_seconds = sleep_t
            elif interval_type == "minutes":
                sleep_seconds = sleep_t * 60
            elif interval_type == "hours":
                sleep_seconds = sleep_t * 3600
            else:
                sleep_seconds = sleep_t

            print(f"⏳ Esperando {sleep_t} {interval_type}...\n")
            for _ in range(int(sleep_seconds)):
                if loop_state["paused"] or not loop_state["active"] or not loop_state["running"]:
                    break
                time.sleep(1)
        else:
            time.sleep(0.5)  # evita consumir CPU innecesario cuando está pausado


def main():
    print(f"\nARGOTH v3.0 — ARRANCANDO (OS: {platform.system()})\n")
    manager = TradeManager(CONFIG)

    loop_state = {"running": True, "active": False, "paused": False}

    # Crear y arrancar el hilo de trading
    thread = threading.Thread(target=trading_loop, args=(manager, loop_state), daemon=True)
    thread.start()

    print("📜 Comandos disponibles: run, pause, resume, stop, status, setdelay <seg>, trade BUY/SELL <symbol> <price> <lot>\n")

    try:
        while loop_state["running"]:
            cmd = input("Comando: ").strip().lower()

            if cmd == "run":
                loop_state["active"] = True
                loop_state["paused"] = False
                print("🚀 Loop automático iniciado.\n")

            elif cmd == "pause":
                loop_state["paused"] = True
                print("⏸️  Pausado.\n")

            elif cmd == "resume":
                loop_state["paused"] = False
                print("▶️  Reanudado.\n")

            elif cmd == "status":
                estado = "Pausado" if loop_state["paused"] else "Activo" if loop_state["active"] else "Detenido"
                print(f"📊 Estado: {estado} | Modo: {manager.mode}\n")

            elif cmd == "stop":
                loop_state["running"] = False
                print("🛑 ARGOTH detenido por usuario.\n")

            elif cmd.startswith("setdelay"):
                try:
                    _, value = cmd.split()
                    manager.delay = int(value)
                    print(f"🧭 Intervalo actualizado a {manager.delay} segundos.\n")
                except Exception:
                    print("⚠ Uso correcto: setdelay <segundos>\n")

            elif cmd.startswith("trade"):
                try:
                    _, trade_type, symbol, price, volume = cmd.split()
                    price = float(price)
                    volume = float(volume)
                    success = manager.broker.place_trade(symbol, trade_type, price, volume)
                    if success:
                        print(f"✅ Trade manual enviado: {trade_type} {symbol} @ {price} vol {volume}\n")
                    else:
                        print("❌ Fallo al enviar trade manual.\n")
                except Exception as e:
                    print(f"⚠ Error al procesar trade manual: {e}\n")

            else:
                print("Comando no reconocido. Usa: run, pause, resume, status, stop, setdelay, trade\n")

    except KeyboardInterrupt:
        print("\n🛑 Stop por teclado.")
        loop_state["running"] = False
    finally:
        manager.shutdown()
        print("🔚 ARGOTH cerrado correctamente.")


if __name__ == "__main__":
    main()