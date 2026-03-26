"""
Sensitivity analysis for SWRO PPP financial model.
"""

from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from .model import SWROMOdel


class SensitivityAnalysis:
    """Sensitivity analysis for SWRO financial models."""

    @staticmethod
    def run_tornado(model: SWROModel, variables=None, metric="lcow"):
        if variables is None:
            variables = {
                "volume_shortfall": (("availability_factor",0.75),("availability_factor",0.95)),
                "capex_overrun": (("capex_per_mld",model.capex_per_mld*0.90),("capex_per_mld",model.capex_per_mld*1.15)),
                "dfi_rate": (("dfi_rate",0.051),("dfi_rate",0.080)),
                "fx_depreciation": (("fx_mxn_usd",21.0),("fx_mxn_usd",16.0)),
                "energy": (("energy_kwh_per_m3",model.energy_kwh_per_m3-0.4),("energy_kwh_per_m3",model.energy_kwh_per_m3+0.6)),
            }
        results = {}
        for var_name, (low_spec, high_spec) in variables.items():
            model_low = model._clone(); setattr(model_low, low_spec[0], low_spec[1])
            model_high = model._clone(); setattr(model_high, high_spec[0], high_spec[1])
            low_m = getattr(model_low, metric); high_m = getattr(model_high, metric)
            results[var_name] = (low_m() if callable(low_m) else low_m, high_m() if callable(high_m) else high_m)
        return results

    @staticmethod
    def sensitivity_table(results, metric_label="LCOW ($/m³)"):
        rows = [[v, f"${l:4f}", f"${h:4f}", f"${abs(h-l):4f}"] for v, (l, h) in results.items()]
        return tabulate(sorted(rows, key=lambda x: float(x[3].replace("$","")), reverse=True),
                         headers=["Variable", "Low", "High", "Range"], tablefmt="grid")

    @staticmethod
    def plot_tornado(results, base_value, figsize=(10,6), output_file=None, x_label="LCOW ($/m³)", title="SWRO Sensitivity Analysis"):
        names = list(results.keys()); lvs = [results[i][0] for i in names]; hvs = [results[i][1] for i in names]
        idx = sorted(range(len(names)), key=lambda i: abs(hvs[i]-lvs[i]), reverse=True)
        names=[names[i] for i in idx]; lvs=[lvs[i] for i in idx]; hvs=[hvs[i] for i in idx]
        fig, ax = plt.subplots(figsize=figsize)
        for i, (n, l, h) in enumerate(zip(names, lvs, hvs)):
            mn, mx = min(l,h), max(l,h)
            ax.barh(i, mn, left=0, color="#d62728", alpha=0.7); ax.barh(i, mx-mn, left=mn, color="#2ca02c", alpha=0.7)
        ax.axvline(base_value, color="black", linestyle="--", linewidth=2)
        ax.set_yticks(range(len(names))); ax.set_yticklabels(names); ax.set_xlabel(x_label); ax.set_title(title)
        plt.tight_layout()
        if output_file: plt.savefig(output_file, dpi=150, bbox_inches="tight")
        return fig
