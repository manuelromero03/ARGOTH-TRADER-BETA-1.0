#utils_ibkr.py
#modulo para registrar operaciones (trades) en CSV 

import csv
from datetime import datetime 
import os 
 
def save_trade_to_db(symbol, action, price):
    """
    Guarda un trade en el archivo 'trades_log.csv'
    """
    file_path = "trades_log.csv"
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Fecha","Simbolo","Accion","Precio"])
        writer.writerow([datetime.now(), symbol, action, price])
        
    print(f"✅ Trade guardado: {symbol} - {action} @ {price}")
    