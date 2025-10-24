# core/risk_manager.py
from config import CONFIG

class RiskManager:
    def __init__(self, cfg=None):
        self.cfg = cfg or CONFIG
        self.initial_capital = self.cfg["capital"]
        self.capital = self.initial_capital
        self.risk_per_trade = self.cfg["risk_per_trade"]
        self.min_lot = self.cfg.get("min_lot", 0.01)
        self.max_lot = self.cfg.get("max_lot", 100.0)
        self.logs = []

    def _log(self, msg):
        """Opcional: guarda logs de decisiones de riesgo"""
        self.logs.append(msg)
        print(f"[RiskManager] {msg}")

    def update_capital(self, pnl):
        """Actualiza el capital disponible según ganancias/perdidas"""
        self.capital += pnl
        self._log(f"Capital actualizado: {self.capital:.2f}")

    def calculate_lot_size(self, price, stop_loss_pips=None, pip_value=None, instrument_type="forex"):
        """
        Calcula lotaje según capital, riesgo y stop-loss.
        Parámetros:
            price: precio actual del instrumento
            stop_loss_pips: si se usa, arriesgará según SL
            pip_value: valor de un pip para el instrumento
            instrument_type: "forex", "index", "stock", "cfd"
        Retorna:
            lot: tamaño de lote válido
        """
        if self.capital <= 0 or price <= 0:
            return self.min_lot

        # Riesgo monetario
        risk_amount = self.capital * self.risk_per_trade

        if stop_loss_pips and pip_value:
            # Riesgo por stop loss
            lot = risk_amount / (stop_loss_pips * pip_value)
        else:
            # Riesgo simple basado en precio (fallback)
            lot = risk_amount / price

        # Aplicar límites del broker
        lot = max(self.min_lot, min(round(lot, 4), self.max_lot))
        self._log(f"Calculated lot: {lot} | Price: {price} | Risk: {risk_amount:.2f}")
        return lot

    def reset_capital(self):
        """Reinicia capital al inicial"""
        self.capital = self.initial_capital
        self._log("Capital reiniciado al valor inicial.")