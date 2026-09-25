"""TrustLens Phase K Execution Script.

Runs the complete read-only Phase K synthesis engine and prints a summary.
"""

from pathlib import Path
import sys

from trustlens.marketplace.final_synthesis import FinalEvidenceSynthesizer

def main():
    base_dir = Path(__file__).resolve().parent.parent
    synthesizer = FinalEvidenceSynthesizer(base_dir=base_dir)
    res = synthesizer.run_all()
    print("---------------------------------------------------------")
    print("TrustLens Phase K Execution Completed.")
    for k, v in res.items():
        print(f"  {k}: {v}")
    print("---------------------------------------------------------")

if __name__ == "__main__":
    main()
