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

          #🧩Parametros avanzados de riesgo (para RiskManager pro)
          "stop_loss_pips": 50,   #tamaño promedio del stop loss en pips
          "pip_value": 10,        #valor por pip en USD (aprox. para 1 lote en forex mayor)
          "min_lot": 0.01,        #tamaño minimo permitido por el broker
          "max_lot": 10.0,        #tamaño maximo permitido por el broker
          "max_daily_loss": 0.05, #5% del capital maximo diario
          "max_drawdown": 0.2,    #20% de perdida maxima total    

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