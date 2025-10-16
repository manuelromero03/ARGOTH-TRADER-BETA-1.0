#core/risk_manager.py
from config import CONFIG

class RiskManager:
    def __init__(self, cfg=None):
        self.cfg= cfg or CONFIG
        self.capital = self.cfg["capital"]
        self.risk_per_trade = self.cfg["risk_per_trade"] 
        
    def calculate_lot_size(self, price):
        """
        Simple: lot = (capital * risk_per_trade) / price
        Nota: en Forex deberias convertir esto a lotes segun su tamaño de contrato.
        """ 
        risk_amount = self.capital * self.risk_per_trade
        if price <= 0:
            return 0.01
        lot = max(0.01, round(risk_amount / price, 4))
        return lot
    