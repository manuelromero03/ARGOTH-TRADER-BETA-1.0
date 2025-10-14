#=========================================
#⚙ CONFIGURACION GLOBAL DE ARGOTH-TRADER
#=========================================]

CONFIG = { 
          #🔷 Modo de operacion
          "mode": "sim", # "sim" = simulador | "real" = MetaTrader5
          
          #🔷 Parametros base 
          "symbol": "EURUSD",
          "capital": 1000,
          "risk_per_trade": 0.01,  #1%
          "take_profit": 0.01,     #1%
          "stop_loss": 0.01,       #1%
          "loop_interval": 10,     #segundos entre cada ciclo
          

          #🔷 Archivos de datos y logs 
          "data_path": "data/precios.csv",
          "signal_log": "data/signals_log.csv",
          "trade_log": "trades_log.csv",
          
          #🔷Configuracion MT5 (solo si mode == "real")
          "mt5_login": 52533292,
          "mt5_password": "6&&@@FDUczlA@K",
          "mt5_server": "ICMarketsInternational-Demo"
}