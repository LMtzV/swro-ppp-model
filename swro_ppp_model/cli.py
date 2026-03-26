"""
CLI for SWRO PPP model
"""
import argparse
import sys
from .model import SWROMOdel
from .sensitivity import SensitivityAnalysis

def main():
    parser = argparse.ArgumentParser(description="SWRO PPP Financial Model")
    parser.add_argument("--capacity", type=float, default=25.0)
    parser.add_argument("--show-sensitivity", action="store_true")
    args = parser.parse_args()
    model = SWROModel(capacity_mld=args.capacity)
    model.print_summary()
    if args.show_sensitivity:
        sensitivity = SensitivityAnalysis()
        results = sensitivity.run_tornado(model)
        print(sensitivity.sensitivity_table(results))

if __name__ == "__main__":
    main()
