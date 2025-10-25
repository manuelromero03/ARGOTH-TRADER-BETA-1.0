import pandas as pd
import importlib
import os
from config import CONFIG
from core.strategy_engine import StrategyEngine
from core.visual_engine import visualEngine
from core.risk_manager import RiskManager
from utils.helpers import safe_print
from utils.utils_sim import get_historical_data, place_trade
import random  # señales temporales para testing

# Intenta detectar MetaTrader5 si mode="auto"
def _detect_mt5_and_set_mode(cfg):
    mode = cfg.get("mode", "auto")
    if mode == "real":
        return "real"
    if mode == "sim":
        return "sim"
    # auto: detect mt5
    try:
        import MetaTrader5 as mt5  # noqa
        return "real"
    except Exception:
        return "sim"


class TradeManager:
    def __init__(self, cfg=None):
        self.cfg = cfg or CONFIG
        self.mode = _detect_mt5_and_set_mode(self.cfg)
        self.symbol = self.cfg["symbol"]
        self.strategy = StrategyEngine(self.cfg)
        self.risk = RiskManager(self.cfg)
        self.visual = visualEngine()
        self.delay = 10  # 🧭 Intervalo en 10 por defecto

        # utils modules
        if self.mode == "real":
            try:
                from utils import utils_mt5 as broker
            except Exception:
                from utils import utils_sim as broker
        else:
            from utils import utils_sim as broker

        self.broker = broker
        safe_print(f"🚀 TradeManager iniciado en modo [{self.mode.upper()}] para {self.symbol}")

    # =======================
    # Registro de riesgo
    # =======================
    def log_risk_info(self, price, lot):
        """Guarda en logs/system_events.log info completa del riesgo y lote calculado"""
        msg = (
            f"{pd.Timestamp.now()} | {self.symbol} | Price: {price} | Calculated lot: {lot} | "
            f"Capital disponible: {self.risk.capital:.2f} | Riesgo por trade: {self.risk.risk_per_trade*100:.2f}%\n"
        )
        with open("logs/system_events.log", "a") as f:
            f.write(msg)
        safe_print(f"[RiskManager] {msg.strip()}")

    # =======================
    # Ciclo principal
    # =======================
    def run_cycle(self):
        os.makedirs("logs", exist_ok=True)
        safe_print("🔁 Iniciando ciclo...")

        # 1) obtener datos
        data = self.broker.get_historical_data(self.symbol)
        if data is None or len(data) == 0:
            safe_print("⚠️ No hay datos. Saltando ciclo.")
            return

        # 2) formatear columnas
        if "Datetime" not in data.columns and data.index.name != "Datetime":
            if "time" in data.columns:
                data = data.rename(columns={"time": "Datetime"})
                data["Datetime"] = pd.to_datetime(data["Datetime"])
                data.set_index("Datetime", inplace=True)

        # 3) calcular indicadores
        data = self.strategy.calculate_indicators(data)
        self.visual.update_data(data)
        self.visual.render()

        # 4) generar señal
        signal = self.strategy.generate_signal(data)

        # 5) calcular lote si hay señal
        if signal:
            stop_loss_pips = self.cfg.get("stop_loss_pips", 50)
            pip_value = self.cfg.get("pip_value", 10)
            price = signal["price"]

            # === 🧠 Nueva lógica de riesgo === #
            lot = self.risk.calculate_lot_size(
                price=price,
                stop_loss_pips=stop_loss_pips,
                pip_value=pip_value,
                instrument_type="forex"
            )
            signal["lot"] = lot

            # registrar info riesgo en logs
            self.risk.log_risk_info(self.symbol, price, lot)

            # === Control de exposición === #
            if not self.risk.can_trade():
                self.risk._log("❌ Operación bloqueada por riesgo. Exposición demasiado alta.")
                with open("logs/system_events.log", "a") as f:
                    f.write(f"{pd.Timestamp.now()} | {self.symbol} | Bloqueado por riesgo\n")
                return

            # ejecutar trade
            self.broker.place_trade(
                self.symbol,
                signal["type"],
                signal["price"],
                lot,
                take_profit=self.cfg["take_profit"],
                stop_loss=self.cfg["stop_loss"],
            )

            # simular resultado (en el futuro conectar con trade real o backtest)
            simulated_pnl = random.uniform(-50, 100)
            self.risk.update_capital(simulated_pnl)

            # Auditoría automática
            try:
                from db_savedate import save_last_commit
                from auto_commit import auto_commit
                save_last_commit()
                auto_commit
            except Exception as e:
                safe_print(f"⚠ Auditoría fallida: {e}")

            safe_print(f"💰 Resultado del trade: {simulated_pnl:+.2f} | Capital actualizado: {self.risk.capital:.2f}")

            # registrar señal
            self.strategy.log_signal(signal, data)
        else:
            # registrar ciclo sin señal
            with open("logs/no_signal.log", "a") as f:
                f.write(f"{pd.Timestamp.now()} | Símbolo: {self.symbol} | No hay señal\n")

        safe_print("✅ Ciclo completado.")

    # =======================
    # Mostrar estado
    # =======================
    def show_status(self):
        safe_print(f"📊 Capital actual: {self.risk.capital:.2f}")
        safe_print(f"📈 Riesgo por trade: {self.risk.risk_per_trade*100:.2f}%")
        safe_print(f"🧩 Modo: {self.mode}")

    # =======================
    # Apagar TradeManager
    # =======================
    def shutdown(self):
        try:
            if self.mode == "real":
                import MetaTrader5 as mt5
                mt5.shutdown()
        except Exception:
            pass
        safe_print("🛑 TradeManager detenido.")