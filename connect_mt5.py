import MetaTrader5 as mt5
from config import CONFIG

def connect_mt5():
    login = CONFIG["mt5"]["login"]
    password = CONFIG["mt5"]["password"]
    server = CONFIG["mt5"]["server"]

    if not mt5.initialize():
        print("❌ No se pudo inicializar MT5.")
        return False

    authorized = mt5.login(login, password, server)
    if not authorized: 
        print(f"❌ Error al iniciar sesion MT5: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    print("✅ Conectado a MT5 ({server}) con login ({login})") 
    return False

if __name__ == "__main__":
    connect_mt5()
    