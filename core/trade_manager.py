# core/trade_manager.py
import pandas as pd
import importlib
from config import CONFIG
from core.strategy_engine import StrategyEngine
from core.visual_engine import visualEngine
from core.risk_manager import RiskManager
from utils.helpers import safe_print
from utils.utils_sim import get_historical_data, place_trade

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
        self.delay = 10 #🧭 Intervalo en 10 por defecto 
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

    def run_cycle(self):
        safe_print("🔁 Iniciando ciclo...")
        # 1) obtener datos
        data = self.broker.get_historical_data(self.symbol)
        if data is None or len(data) == 0:
            safe_print("⚠️ No hay datos. Saltando ciclo.")
            return

        # ensure column names compatible (Datetime index + Open/High/Low/Close/Volume)
        if "Datetime" not in data.columns and data.index.name != "Datetime":
            # try rename time->Datetime or time->index -> Datetime
            if "time" in data.columns:
                data = data.rename(columns={"time": "Datetime"})
                data["Datetime"] = pd.to_datetime(data["Datetime"])
                data.set_index("Datetime", inplace=True)

        # 2) calcular indicadores
        data = self.strategy.calculate_indicators(data)

        self.visual.update_data(data)
        self.visual.render()

        # 3) generar señal (dict or None)
        signal = self.strategy.generate_signal(data)

        # 4) calcular lote
        lot = None
        if signal:
            lot = self.risk.calculate_lot_size(price=signal["price"])
            signal["lot"] = lot

        # 5) ejecutar trade
        if signal:
            self.broker.place_trade(
                self.symbol,
                signal["type"],
                signal["price"],
                lot,
                take_profit=self.cfg["take_profit"],
                stop_loss=self.cfg["stop_loss"],
            )

        # 6) log (strategy can also log)
        self.strategy.log_signal(signal, data)

        safe_print("✅ Ciclo completado.")

    def shutdown(self):
        # broker-specific shutdown
        try:
            if self.mode == "real":
                import MetaTrader5 as mt5
                mt5.shutdown()
        except Exception:
            pass
