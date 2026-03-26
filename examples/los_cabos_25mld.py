"""
Los Cabos 25 MLD SWRO Project Example
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from swro_ppp_model import SWROModel
from swro_ppp_model.sensitivity import SensitivityAnalysis


def main():
    print("\nLOS CABOS 25 MLD SWRO PPP MODEL\n" + "="*60)

    base = SWSOModel(capacity_mld=25, capex_per_mld=1_500_000, dfi_rate=0.065, target_equity_irr=0.162)
    base.print_summary()

    cons = SWROMOdel(capacity_mld=25, capex_per_mld=1_725_000, dfi_rate=0.075, availability_factor=0.75, fx_mxn_usd=21.0)
    print("\nCONSERVATIVE CASE:")
    cons.print_summary()

    print(f"\nKey: Base LCOW ${base.lcow():.3f}/m³ | Conservative ${cons.lcow():.3f}/m³")
    s = SensitivityAnalysis()
    print(s.sensitivity_table(s.run_tornado(base)))


if __name__ == "__main__":
    main()
