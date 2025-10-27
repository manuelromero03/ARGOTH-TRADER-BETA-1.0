# core/risk_manager.py
"""
RiskManager v3 — avanzado
- Controla capital, riesgo por trade, límites diarios y drawdown.
- Ajusta riesgo dinámicamente según rendimiento y volatilidad.
- Persiste métricas en sqlite (data/argoth_system.db).
- API simple para integrar con TradeManager.
"""

from __future__ import annotations
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from utils import utils_mt5  # importar utils_mt5 al inicio del archivo
from config import CONFIG
import pandas as pd

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "argoth_system.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class RiskManager:
    def __init__(self, cfg=None):
        self.cfg = cfg or CONFIG
        # ⚡ Detectar capital inicial real si estamos en modo MT5
        try:
            if self.cfg.get("mode") == "real":
                import utils.utils_mt5 as utils_mt5  # asegúrate de importar aquí
                balance = utils_mt5.get_account_balance()
                self.initial_capital = float(balance) if balance is not None else float(self.cfg.get("capital", 1000.0))
            else:
                self.initial_capital = float(self.cfg.get("capital", 1000.0))
        except Exception as e:
            print(f"⚠️ No se pudo detectar capital real: {e}")
            self.initial_capital = float(self.cfg.get("capital", 1000.0))

        # Asignar capital inicial
        self.capital = float(self.initial_capital)
        self.risk_per_trade = float(self.cfg.get("risk_per_trade", 0.01))
        self.min_lot = float(self.cfg.get("min_lot", 0.01))
        self.max_lot = float(self.cfg.get("max_lot", 100.0))

        # límites
        self.max_daily_loss = float(self.cfg.get("max_daily_loss", 0.05))
        self.max_drawdown = float(self.cfg.get("max_drawdown", 0.20))

        # trackers en runtime
        self.daily_pnl = 0.0
        self.equity_high = self.initial_capital
        self.logs = []

        # Inicializar DB si existe
        self._init_db()

    def show_params(self):
        print(f"✅ Capital inicial: {self.initial_capital} USD")
        print(f"✅ Riesgo por trade: {self.risk_per_trade * 100}%")
        print(f"✅ StopLoss/TakeProfit: configurados ({self.cfg.get('stop_loss', 0.01)} = 1%)")
        print(f"✅ Lotes minimos/maximos: {self.max_daily_loss * 100:.0f}%")
        print(f"✅ Max. perdidas diaria: {self.max_daily_loss * 100:.0f}%")
        print(f"✅ Max. drawdowm total: {self.max_drawdown * 100:.0f}%")

    # ---------- Internal helpers ----------
    def _log(self, msg: str):
        """Registro simple en memoria + stdout para depuración."""
        ts = datetime.now().isoformat(sep=" ", timespec="seconds")
        line = f"[{ts}] {msg}"
        self.logs.append(line)
        print(f"[RiskManager] {msg}")

    def _init_db(self):
        """Crea la tabla de métricas si no existe."""
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
        """Guarda snapshot de métricas en la DB local."""
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

    # ---------- Public API ----------
    def update_capital(self, pnl: float):
        """
        Actualiza capital y trackers luego de cerrar una operación.
        pnl: beneficio (positivo) o pérdida (negativo)
        """
        self.capital += pnl
        self.daily_pnl += pnl

        # actualizar equity_high
        if self.capital > self.equity_high:
            self.equity_high = self.capital

        self._log(f"Capital actualizado: {self.capital:.2f} (pnl {pnl:+.2f})")
        # persistir métricas
        self._save_metrics_db()

    def reset_daily(self):
        """Resetea contador diario de PnL (llamar al inicio de día/trading session)."""
        self._log(f"Reset diario: previous daily_pnl={self.daily_pnl:.2f}")
        self.daily_pnl = 0.0
        self._save_metrics_db()

    def calculate_lot_size(
        self,
        price: float,
        stop_loss_pips: Optional[float] = None,
        pip_value: Optional[float] = None,
        instrument_type: str = "forex",
    ) -> float:
        """
        Calcula el lote a enviar.
        - Si se suministra stop_loss_pips & pip_value usa formula basada en SL.
        - Si no, usa risk_amount/price como fallback (no ideal para forex en reales).
        """
        if self.capital <= 0 or price <= 0:
            return self.min_lot

        risk_amount = self.capital * self.risk_per_trade

        if stop_loss_pips is not None and pip_value is not None and stop_loss_pips > 0:
            lot = risk_amount / (stop_loss_pips * pip_value)
        else:
            # Fallback: riesgo relativo al precio (útil para activos no-forex)
            lot = risk_amount / price

        lot = max(self.min_lot, min(round(float(lot), 4), self.max_lot))
        self._log(f"Calculated lot: {lot} | price: {price} | risk_amount: {risk_amount:.2f}")
        return lot

    def adjust_risk_based_on_performance(self):
        """
        Ajusta el porcentaje de riesgo por trade en función del rendimiento relativo
        al capital inicial.
        - Si ganamos +10% aumenta ligeramente riesgo (scaling up).
        - Si perdemos -10% reduce riesgo (scaling down).
        """
        try:
            ratio = self.capital / self.initial_capital
            old = self.risk_per_trade
            if ratio >= 1.10:
                self.risk_per_trade = min(self.risk_per_trade * 1.15, 0.05)  # cap 5%
            elif ratio <= 0.90:
                self.risk_per_trade = max(self.risk_per_trade * 0.8, 0.002)  # floor 0.2%
            if old != self.risk_per_trade:
                self._log(f"Riesgo ajustado de {old:.4f} -> {self.risk_per_trade:.4f}")
                self._save_metrics_db()
        except Exception as e:
            self._log(f"ERROR ajustando riesgo: {e}")

    def adjust_for_volatility(self, atr_value: Optional[float]):
        """
        Ajusta el riesgo si detectamos alta volatilidad (por ejemplo usando ATR).
        atr_value: valor ATR normalizado para el instrumento (p. ej. porcentaje).
        """
        if atr_value is None:
            return
        try:
            # ejemplo: si ATR por encima de umbral, reducir riesgo
            threshold = float(self.cfg.get("volatility_atr_threshold", 0.01))
            if atr_value > threshold:
                old = self.risk_per_trade
                self.risk_per_trade = max(0.001, self.risk_per_trade * 0.7)
                self._log(f"Alta volatilidad (ATR={atr_value:.4f}) -> riesgo {old:.4f} -> {self.risk_per_trade:.4f}")
                self._save_metrics_db()
        except Exception as e:
            self._log(f"ERROR ajuste volatilidad: {e}")

    def can_trade(self) -> bool:
        """
        Evalúa si se permiten nuevas operaciones:
        - no operar si drawdown > max_drawdown
        - no operar si pérdida diaria > max_daily_loss
        """
        try:
            drawdown = 0.0
            if self.equity_high > 0:
                drawdown = 1.0 - (self.capital / self.equity_high)
            if drawdown > self.max_drawdown:
                self._log(f"BLOCK: drawdown {drawdown:.3f} > max_drawdown {self.max_drawdown:.3f}")
                return False
            if self.daily_pnl < -abs(self.initial_capital * self.max_daily_loss):
                self._log(f"BLOCK: daily_pnl {self.daily_pnl:.2f} < -{self.initial_capital * self.max_daily_loss:.2f}")
                return False
            return True
        except Exception as e:
            self._log(f"ERROR can_trade eval: {e}")
            return False

    def log_metrics(self) -> Dict[str, float]:
        """Devuelve y guarda métricas actuales (útil para dashboards)."""
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

    def log_risk_info(self, symbol: str, price: float, lot: float):
        """
        Guarda en logs/system_events.log información completa del riesgo y lote calculado.
        """
        msg = (
            f"{pd.Timestamp.now()} | {symbol} | Price: {price} | "
            f"Calculated lot: {lot} | Capital disponible: {self.capital:.2f} | "
            f"Riesgo por trade: {self.risk_per_trade*100:.2f}%\n"
        )
        # escribir en archivo
        os.makedirs("logs", exist_ok=True)
        with open("logs/system_events.log", "a") as f:
            f.write(msg)
        # imprimir en consola
        print(f"[RiskManager] {msg.strip()}")

    def reset_capital(self):
        """Reinicia capital al valor inicial (para testing)."""
        self.capital = float(self.initial_capital)
        self.daily_pnl = 0.0
        self.equity_high = float(self.initial_capital)
        self._log("Capital reiniciado al inicial.")
        self._save_metrics_db()
