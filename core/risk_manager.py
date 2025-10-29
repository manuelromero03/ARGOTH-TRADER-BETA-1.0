# core/risk_manager.py
"""
RiskManager v3.1 — avanzado
- Detecta capital real en MT5 o inicializa desde configuración.
- Mantiene capital actualizado en cada ciclo.
- Controla riesgo por trade, límites diarios y drawdown.
- Persiste métricas en sqlite (data/argoth_system.db).
"""

from __future__ import annotations
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
from config import CONFIG

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "argoth_system.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class RiskManager:
    def __init__(self, cfg=None):
        self.cfg = cfg or CONFIG
        self.mode = self.cfg.get("mode", "sim")

        # ⚡ Capital inicial: detecta MT5 si estamos en modo real
        self.initial_capital = self._detect_initial_capital()
        self.capital = float(self.initial_capital)

        # Configuración riesgo y lotes
        self.risk_per_trade = float(self.cfg.get("risk_per_trade", 0.01))
        self.min_lot = float(self.cfg.get("min_lot", 0.01))
        self.max_lot = float(self.cfg.get("max_lot", 100.0))

        # Límites
        self.max_daily_loss = float(self.cfg.get("max_daily_loss", 0.05))
        self.max_drawdown = float(self.cfg.get("max_drawdown", 0.20))

        # Trackers runtime
        self.daily_pnl = 0.0
        self.equity_high = self.initial_capital
        self.logs = []

        # Inicializar DB
        self._init_db()

    # =======================
    # Capital / sincronización
    # =======================
    def _detect_initial_capital(self) -> float:
        """Detecta capital inicial desde MT5 o configuración."""
        try:
            if self.mode == "real":
                from utils import utils_mt5
                balance = utils_mt5.get_account_balance()
                if balance is not None:
                    return float(balance)
        except Exception as e:
            print(f"⚠️ No se pudo detectar capital real: {e}")
        # fallback: usar valor de config
        return float(self.cfg.get("capital", 1000.0))

    def sync_with_account(self):
        """Actualiza capital con balance real de MT5 si estamos en modo real."""
        if self.mode != "real":
            return
        try:
            from utils import utils_mt5
            balance = utils_mt5.get_account_balance()
            if balance is not None:
                self.capital = float(balance)
                self.initial_capital = float(balance)  # opcional: reset inicial
                self._log(f"Capital sincronizado con cuenta real: {self.capital:.2f}")
        except Exception as e:
            self._log(f"ERROR sync_with_account: {e}")

    # =======================
    # Métodos de logging y DB
    # =======================
    def _log(self, msg: str):
        ts = datetime.now().isoformat(sep=" ", timespec="seconds")
        line = f"[{ts}] {msg}"
        self.logs.append(line)
        print(f"[RiskManager] {msg}")

    def _init_db(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS risk_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    capital REAL,
                    risk_per_trade REAL,
                    daily_pnl REAL,
                    equity_high REAL,
                    max_drawdown REAL,
                    max_daily_loss REAL
                )
                """
            )
            conn.commit()
        except Exception as e:
            self._log(f"ERROR init db: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _save_metrics_db(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO risk_metrics
                (timestamp, capital, risk_per_trade, daily_pnl, equity_high, max_drawdown, max_daily_loss)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(sep=" ", timespec="seconds"),
                    float(self.capital),
                    float(self.risk_per_trade),
                    float(self.daily_pnl),
                    float(self.equity_high),
                    float(self.max_drawdown),
                    float(self.max_daily_loss),
                ),
            )
            conn.commit()
        except Exception as e:
            self._log(f"ERROR saving metrics to DB: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # =======================
    # API pública
    # =======================
    def show_params(self):
        print(f"✅ Capital inicial: {self.initial_capital} USD")
        print(f"✅ Riesgo por trade: {self.risk_per_trade*100:.2f}%")
        print(f"✅ Max. perdidas diaria: {self.max_daily_loss*100:.2f}%")
        print(f"✅ Max. drawdowm total: {self.max_drawdown*100:.2f}%")

    def update_capital(self, pnl: float):
        """Actualiza capital y trackers luego de cerrar operación."""
        self.capital += pnl
        self.daily_pnl += pnl
        if self.capital > self.equity_high:
            self.equity_high = self.capital
        self._log(f"Capital actualizado: {self.capital:.2f} (pnl {pnl:+.2f})")
        self._save_metrics_db()

    def reset_daily(self):
        self._log(f"Reset diario: previous daily_pnl={self.daily_pnl:.2f}")
        self.daily_pnl = 0.0
        self._save_metrics_db()

    def calculate_lot_size(
        self, price: float, stop_loss_pips: Optional[float]=None,
        pip_value: Optional[float]=None, instrument_type: str="forex"
    ) -> float:
        if not isinstance(price, (int, float)):
            raise TypeError(f"Price debe ser numero, no {type(price)}: {price}")
        if price <= 0:
            raise ValueError(f"Price debe ser mayor a 0, no {price}")
        if stop_loss_pips <= 0 or pip_value <= 0:
            raise ValueError("stop_loss_pips y pip_value deben ser mayores a 0")
        if self.capital <= 0 or price <= 0:
            return self.min_lot
        risk_amount = self.capital * self.risk_per_trade
        if stop_loss_pips and pip_value:
            lot = risk_amount / (stop_loss_pips * pip_value)
        else:
            lot = risk_amount / price
        lot = max(self.min_lot, min(round(float(lot),4), self.max_lot))
        self._log(f"Calculated lot: {lot} | price: {price} | risk_amount: {risk_amount:.2f}")
        return lot

    def can_trade(self) -> bool:
        try:
            drawdown = 0.0
            if self.equity_high > 0:
                drawdown = 1.0 - (self.capital / self.equity_high)
            if drawdown > self.max_drawdown:
                self._log(f"BLOCK: drawdown {drawdown:.3f} > max_drawdown {self.max_drawdown:.3f}")
                return False
            if self.daily_pnl < -abs(self.initial_capital * self.max_daily_loss):
                self._log(f"BLOCK: daily_pnl {self.daily_pnl:.2f} < -{self.initial_capital*self.max_daily_loss:.2f}")
                return False
            return True
        except Exception as e:
            self._log(f"ERROR can_trade eval: {e}")
            return False

    def log_metrics(self) -> Dict[str,float]:
        metrics = {
            "capital": float(self.capital),
            "risk_per_trade": float(self.risk_per_trade),
            "daily_pnl": float(self.daily_pnl),
            "equity_high": float(self.equity_high),
            "max_drawdown": float(self.max_drawdown),
            "max_daily_loss": float(self.max_daily_loss),
            "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds"),
        }
        self._log(f"Métricas: {metrics}")
        self._save_metrics_db()
        return metrics

    def reset_capital(self):
        self.capital = float(self.initial_capital)
        self.daily_pnl = 0.0
        self.equity_high = float(self.initial_capital)
        self._log("Capital reiniciado al inicial.")
        self._save_metrics_db()