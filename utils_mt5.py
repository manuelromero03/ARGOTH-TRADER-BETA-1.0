# utils_mt5.py 
# Modulo encargado de obtener precios del mercado (simulador por ahora)

import random 

def get_price_mt5(symbol, n=200):
    """
    Simula la obtencion de los ultimos n precios para un simbolo dado 
    Mas adelante se conectara con MetaTrader 5 o una API Real 
    """ 
    
    base_price = 50000  # precio base de ejemplo
    prices = [base_price + random.uniform(-1000, 1000) for _ in range(n)]
    return prices