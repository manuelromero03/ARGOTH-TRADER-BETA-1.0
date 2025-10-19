import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
import pandas as pd 

class visualEngine:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.ax.set_title("ARGOTH Visual Engine - Modo Simulador")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Precio")

        self.data = pd.DataFrame()
        self.buy_signals = []
        self.sell_siganls = []

    def update_data(self, df, buy_signals=None, sell_signals=None):
        self.data = df 
        self.buy_signals = buy_signals or []
        self.sell_siganls = sell_signals or []

    def render(self):
        if self.data.empty:
            return
        
        self.ax.clear()
        self.ax.plot(self.data["Datetime"], self.data["Close"], label="Precio", color="white")

        for idx in self.buy_signals:
            self.ax.scatter(self.data["Datetime"].iloc[idx], self.data["Close"].iloc[idx],
                            color="lime", marker="v", label="SELL")
            
            self.ax.legend()
            plt.pause(0.1)