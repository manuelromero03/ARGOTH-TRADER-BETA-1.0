# utils/data_handler.py
import pandas as pd
import os
from datetime import datetime

DATA_DIR =os.path.join(os.path.dirname(__file__), '..', 'data')
PRICE_FILE = os.path.join(DATA_DIR, "precios.csv")
SIGNALS_FILE = os.path.join(DATA_DIR, "signals_log.csv")

class DataHandler:
    def __init__(self):
        #Cargar precios si existen
        if os.path.exists(PRICE_FILE):
            self.prices = pd.read_csv(PRICE_FILE, index_col=0, parse_dates=True)
        else:
            self.price_data = pd.DataFrame()

        #Cargar señales si existen
        if os.path.exists(SIGNALS_FILE):
            self.signals = pd.read.csv(SIGNALS_FILE, index_col=0, parse_dates=True)
        else:
            self.signals = pd.DataFrame()

    def get_price(self, symbol: str, interval: str="1m"):
        """
        Retorna precios recientes de un simbolo.
        - symbol: ticker (ej: "EURUSD", "AAPL")
        - interval: "1m", "5m", "1h", etc.
        """
        if self.prices.empty: 
            return pd.DataFrame()
        
        df = self.prices[self.prices["symbol"] == symbol].copy()
        df = df.set_index("datetime").sort_index()
        #Filtrar Intervalo si es necesario (a implementar)
        return df
    
    def save_price(self, symbol: str, datetime_obj: datetime, price: float):
        """
        Guarda un nuevo precio en el archivo CSV.   
        """
        new_row = {"symbol": symbol, "datetime": datetime_obj, "price": price}
        self.prices = pd.concat([self.prices, pd.DataFrame([new_row])], ignore_index=True)
        self.prices.to_csv(PRICE_FILE, index=False)

    def save_signal(self, symbol: str, signal_type: str ,price: float, volume: float):
        """
        Guarda una señal generada por la estrategia.
        """
        new_signal = {
            "datetime": datetime.now(),
            "symbol": symbol,
            "signal": signal_type,
            "price": price,
            "volume": volume              
        }
        self.signals = pd.concat([self.signals, pd.DataFrame(new_signal)], ignore_index=True)
        self.signals.to_csv(SIGNALS_FILE, index=False)

