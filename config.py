#=========================================
#⚙ CONFIGURACION GLOBAL DE ARGOTH-TRADER
#=========================================]

CONFIG = { 
          #modo: "sim" (simulador), "real" (forzar MT5) o "auto" (intenta conectar MT5)
          "mode": "auto",          
          
          #parametros de cuenta y riesgo
          "symbol": "EURUSD",
          "capital": 1000.0,
          "risk_per_trade": 0.01, #1%
          "take_profit": 0.01,    #1%
          "stop_loss": 0.01,      #1%
                    
          #Loop / timing
          "interval_type": "seconds", #"secunds", "minutes", "hours"
          "interval_value": 10, #valor base
          
          #archivos 
          "data_path": "data/precios.csv",
          "signals_log": "data/signal_log.csv",
          "trades_log": "data/trades_log.csv",
                    
          #🔷Configuracion MT5 (solo si mode == "real")
          "mt5":{
            "login": 52533292,
            "password": "6&&@@FDUczlA@K",
            "server": "ICMarketsInternational-Demo"    
          }         
}