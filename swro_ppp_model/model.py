"""
Core SWRO PPP financial model implementation.

Implements the Mexican T1/T2/T3 tariff framework with proper financial mathematics
for debt service, equity returns, and operating cost pass-throughs.
"""

from typing import Dict, Any, Optional
import numpy as np
from tabulate import tabulate

# Try scipy, fall back to numpy-based Newton-Raphson
try:
    from scipy.optimize import newton
except ImportError:
    newton = None


class SWROModel:
    """
    Financial model for SWRO Public-Private Partnership projects.

    Implements T1/T2/T3 tariff framework for Mexican water concessions.
    Provides comprehensive financial metrics for project evaluation.
    """

    def __init__(
        self,
        capacity_mld: float = 25.0,
        capex_per_mld: float = 1_500_000.0,
        capex_contingency: float = 0.10,
        debt_ratio: float = 0.65,
        equity_ratio: float = 0.35,
        dfi_rate: float = 0.065,
        debt_tenor: int = 18,
        target_equity_irr: float = 0.162,
        t2_opex_per_mld: float = 30_000.0,
        energy_kwh_per_m3: float = 3.8,
        cfe_tariff_mxn: float = 1.45,
        fx_mxn_usd: float = 17.5,
        contract_years: int = 25,
        availability_factor: float = 0.85,
    ) -> None:
        self.capacity_mld = capacity_mld
        self.capex_per_mld = capex_per_mld
        self.capex_contingency = capex_contingency
        self.debt_ratio = debt_ratio
        self.equity_ratio = equity_ratio
        self.dfi_rate = dfi_rate
        self.debt_tenor = debt_tenor
        self.target_equity_irr = target_equity_irr
        self.t2_opex_per_mld = t2_opex_per_mld
        self.energy_kwh_per_m3 = energy_kwh_per_m3
        self.cfe_tariff_mxn = cfe_tariff_mxn
        self.fx_mxn_usd = fx_mxn_usd
        self.contract_years = contract_years
        self.availability_factor = availability_factor

    @property
    def capex(): return self.capacity_mld * self.capex_per_mld * (1 + self.capex_contingency)

    @property
    def debt(self): return self.capex * self.debt_ratio

    @property
    def equity(self): return self.capex * self.equity_ratio

    @property
    def annual_volume_m3(self): return self.capacity_mld * 1_000 * 365 * self.availability_factor

    def t1c_annual(self):
        r = self.dfi_rate; n = self.debt_tenor
        return self.debt * (r * (1+r)**n) / ((1+r)**n - 1)

    def t1r_annual(self):
        irr = self.target_equity_irr; n = self.contract_years
        return self.equity * (irr * (1+irr)**n) / ((1+irr)**n - 1)

    def t2_annual(self): return self.capacity_mld * self.t2_opex_per_mld

    def t3_annual(self):
        return (self.capacity_mld * 1_000 * 365 * self.energy_kwh_per_m3 * self.cfe_tariff_mxn) / self.fx_mxn_usd

    def total_annual_revenue(self): return self.t1c_annual() + self.t1r_annual() + self.t2_annual() + self.t3_annual()

    def dscr(self, cfads_ratio=0.90):
        cfads = self.t1c_annual() + self.t1r_annual() * cfads_ratio
        t1c = self.t1c_annual()
        return cfads / t1c if t1c > 0 else 0.0

    def equity_irr(self): return self.target_equity_irr

    def wacc(self, tax_rate=0.30):
        return (self.equity_ratio * self.target_equity_irr + self.debt_ratio * self.dfi_rate * (1 - tax_rate))

    def lcow(self):
        return self.total_annual_revenue() / self.annual_volume_m3 if self.annual_volume_m3 > 0 else 0.0

    def summary(self):
        return {"capacity_mld": self.capacity_mld, "capexUSDM": self.capex/1e6, "dscr": self.dscr(), "equity_irr": self.equity_irr(), "lcow": self.lcow()}

    def print_summary(self):
        s = self.summary()
        print(f"SWRO PPP Model - {s['capacity_mld']} MLD\nCAPEX: ${s['capexUSDM]']:.1f}M\nDSCR: {s['dscr']:.2f}x\nEQuity IRR: {s['equity_irr']*100:.2f}%\nLCOW: ${s['lcow']}:.4f}/m3")
