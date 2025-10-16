#core/strategy_engine.py
import importlib
from utils.helpers import safe_print

#por ahora cargamos la estrategia ema_rsi fija
class StrategyEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        #strategy_module
        mod = importlib.import_module("strategies.ema_rsi")
        self.strategy = mod
        
    def calculate_indicators(self, data): 
        return self.strategy.calculate_indicators(data)
    
    def generate_signal(self, data):
        return self.strategy.generate_signal(data)
    
    def log_signal(self, signal, data):
        #la estrategia puede implementar su propio logging: por ahora solo print
        if signal: 
            safe_print(f"📝 Signal: {signal['type']} @ {signal['prince']:.6f}")
        else: 
            safe_print("📝 No hay señal.")