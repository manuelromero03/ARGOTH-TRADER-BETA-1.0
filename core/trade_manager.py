import pandas as pd
import importlib
import os
import random
from config import CONFIG
from core.strategy_engine import StrategyEngine
from core.visual_engine import visualEngine
from core.risk_manager import RiskManager
from utils.helpers import safe_print
from utils.utils_sim import get_historical_data, place_trade

def _detect_mt5_and_set_mode(cfg):
    """Detecta si se puede usar MT5 real, sino cae en sim."""
    mode = cfg.get("mode", "auto")
    if mode in ["real", "sim"]:
        return mode
    try:
        import MetaTrader5 as mt5
        return "real"
    except Exception:
        return "sim"

class TradeManager:
    def __init__(self, cfg=None):
        self.cfg = cfg or CONFIG
        self.mode = _detect_mt5_and_set_mode(self.cfg)
        self.symbol = self.cfg["symbol"]
        self.strategy = StrategyEngine(self.cfg)
       
        # Instanciamos RiskManager
        self.risk_manager = RiskManager(self.cfg)

        # Sincronizar capital con MT5 si estamos en modo real
        if self.mode == "real":
            self.risk_manager.sync_with_account()

        # Visualización y loop
        self.visual = visualEngine()
        self.delay = 10  # 🧭 Intervalo por defecto

        # Inicializar broker
        try:
            if self.mode == "real":
                from utils import utils_mt5 as broker
            else:
                from utils import utils_sim as broker
        except Exception:
            from utils import utils_sim as broker
            safe_print("⚠️ No se pudo cargar MT5, usando simulación")

        self.broker = broker

        # Conectar MT5 si estamos en modo real
        if self.mode == "real":
            from utils import utils_mt5
            utils_mt5.connect_mt5(self.cfg)

        # ✅ Mostramos estado inicial (una sola vez)
        safe_print(f"🚀 TradeManager iniciado en modo [{self.mode.upper()}] para {self.symbol}")
        self.risk_manager.show_params()

    # =======================
    # Registro de riesgo
    # =======================
    def record_risk(self, price, lot):
        """Guarda métricas de riesgo y lote en logs."""
        os.makedirs("logs", exist_ok=True)
        msg = (
            f"{pd.Timestamp.now()} | {self.symbol} | Price: {price} | Calculated lot: {lot} | "
            f"Capital disponible: {self.risk_manager.capital:.2f} | Riesgo por trade: {self.risk_manager.risk_per_trade*100:.2f}%\n"
        )
        with open("logs/system_events.log", "a") as f:
            f.write(msg)
        safe_print(f"[RiskManager] {msg.strip()}")

        # registrar métricas generales en la DB
        self.risk_manager.log_metrics()

    # =======================
    # Ciclo principal
    # =======================
    def run_cycle(self):
        os.makedirs("logs", exist_ok=True)
        safe_print("🔁 Iniciando ciclo...")

        # 1) Sincronizar capital real antes de cada ciclo
        if self.mode == "real":
            self.risk_manager.sync_with_account()

        # 2) Obtener datos históricos
        data = self.broker.get_historical_data(self.symbol)
        if data is None or len(data) == 0:
            safe_print("⚠️ No hay datos. Saltando ciclo.")
            return

        # 3) Formatear columnas si es necesario
        if "Datetime" not in data.columns and data.index.name != "Datetime":
            if "time" in data.columns:
                data = data.rename(columns={"time": "Datetime"})
                data["Datetime"] = pd.to_datetime(data["Datetime"])
                data.set_index("Datetime", inplace=True)

        # 4) Calcular indicadores y actualizar visualización
        data = self.strategy.calculate_indicators(data)
        self.visual.update_data(data)
        self.visual.render()

        # 5) Generar señal según estrategia
        signal = self.strategy.generate_signal(data)

        # ===== 6) Calcular lote y registrar métricas de riesgo siempre =====
        stop_loss_pips = self.cfg.get("stop_loss_pips", 50)
        pip_value = self.cfg.get("pip_value", 10)
        last_price = data["close"].iloc[-1] if "close" in data.columns else data.iloc[-1, 0]

        lot = self.risk_manager.calculate_lot_size(
            price=last_price,
            stop_loss_pips=stop_loss_pips,
            pip_value=pip_value,
            instrument_type="forex"
        )

        self.record_risk(last_price, lot)

        # ===== 7) Si hay señal, ejecutar trade =====
        if signal:
            signal["lot"] = lot

            if not self.risk_manager.can_trade():
                self.risk_manager._log("❌ Operación bloqueada por riesgo. Exposición demasiado alta.")
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

            simulated_pnl = random.uniform(-50, 100)
            self.risk_manager.update_capital(simulated_pnl)

            safe_print(f"💰 Resultado del trade: {simulated_pnl:+.2f} | Capital actualizado: {self.risk_manager.capital:.2f}")
            self.strategy.log_signal(signal, data)
        else:
            with open("logs/no_signal.log", "a") as f:
                f.write(f"{pd.Timestamp.now()} | Símbolo: {self.symbol} | No hay señal\n")
            safe_print(f"ℹ️ No hay señal, pero métricas de riesgo calculadas.")

        safe_print("✅ Ciclo completado.")

    # =======================
    # Mostrar estado
    # =======================
    def show_status(self):
        safe_print(f"📊 Capital actual: {self.risk_manager.capital:.2f}")
        safe_print(f"📈 Riesgo por trade: {self.risk_manager.risk_per_trade*100:.2f}%")
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