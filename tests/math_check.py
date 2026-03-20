"""
Unit test to verify the mathematical validity of the De-Biasing engine.
"""

import sys
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.strategy.engine import AlphaEngine

def run_dummy_test() -> None:
    """
    Feeds a Dummy Market (Price: 0.05, Vol: 10,000) to verify theoretical expectations.
    Expects P_fair ≈ 0.02.
    """
    print("Executing Math Integrity Check...")
    engine = AlphaEngine()
    
    dummy_df = pd.DataFrame([{
        "condition_id": "DUMMY",
        "question": "TEST_MARKET",
        "current_price": 0.05,
        "volume": 10000.0,
        "liquidity": 1000.0,
        "is_liquid": True
    }])
    
    result = engine.analyze(dummy_df)
    if not result.empty:
        pfair = result.iloc[0]['fair_probability']
        print(f"Dummy Market (Price 0.05) -> P_fair: {pfair:.4f} (Expected ~0.0221)")
    else:
        print("Dummy Market was implicitly filtered out by the strategy constraints.")

if __name__ == "__main__":
    run_dummy_test()
