"""
Heuristic Alpha Main Driver.

Fetches live market data from Polymarket, evaluates probabilities
through the AlphaEngine, and outputs the top arbitrage signals.
"""

import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from tabulate import tabulate

from src.data.fetcher import PolymarketFetcher
from src.strategy.engine import AlphaEngine

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def _assign_trade_rating(strength: float, max_strength: float) -> str:
    """Assigns a visual 1-5 star rating based on relative signal strength."""
    if max_strength <= 0: return "★☆☆☆☆"
    ratio = strength / max_strength
    if ratio > 0.8: return "★★★★★"
    if ratio > 0.6: return "★★★★☆"
    if ratio > 0.4: return "★★★☆☆"
    if ratio > 0.2: return "★★☆☆☆"
    return "★☆☆☆☆"

async def main() -> None:
    load_dotenv()
    print("Initializing Heuristic Alpha Pipeline...")
    
    # Secure key fetch without hardcoding
    api_key = os.getenv("POLYMARKET_API_KEY")
    api_secret = os.getenv("POLYMARKET_SECRET")
    api_passphrase = os.getenv("POLYMARKET_PASSPHRASE")
    
    fetcher = PolymarketFetcher()
    engine = AlphaEngine()
    
    print("\nFetching active markets from Polymarket CLOB...")
    
    max_retries = 3
    df_markets = pd.DataFrame()
    for attempt in range(max_retries):
        try:
            df_markets = await fetcher.fetch_markets()
            if not df_markets.empty:
                break
            print(f"Warning: API returned empty list. Retrying... ({attempt+1}/{max_retries})")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error fetching data: {e}. Retrying... ({attempt+1}/{max_retries})")
            await asyncio.sleep(2)
            
    if df_markets.empty:
        print("CRITICAL: Failed to retrieve market data after multiple retries. Exiting.")
        return
        
    print(f"Fetched {len(df_markets)} active markets. Engaging analysis...")
    
    df_opportunities = engine.analyze(df_markets)
    
    # Global irrationality indicator
    df_markets['fair_probability'] = engine.prospect_engine.get_fair_probability(df_markets['current_price'])
    p_fair_safe = np.clip(df_markets['fair_probability'], 1e-9, None)
    df_markets['alpha_edge'] = (df_markets['current_price'] - df_markets['fair_probability']) / p_fair_safe
    market_rationality_score = engine.prospect_engine.calculate_market_rationality(df_markets['alpha_edge'])
    
    if df_opportunities.empty:
        print("No positive Alpha Edge opportunities active currently.")
        print(f"\nAverage Market Cognitive Friction: {market_rationality_score:.2f}%")
        return
        
    print("Analysis complete. Displaying Top 10 Signals:")
    print("-" * 130)
    
    top_10 = df_opportunities.head(10).copy()
    max_sig = top_10['signal_strength'].max()
    
    top_10['Trade Rating'] = top_10['signal_strength'].apply(lambda x: _assign_trade_rating(x, max_sig))
    
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    top_10['Timestamp'] = run_timestamp
    
    top_10 = top_10.rename(columns={
        'question': 'Market Name',
        'current_price': 'Market Price',
        'fair_probability': 'De-Biased Price',
        'alpha_edge': 'Alpha %',
        'bias_type': 'Bias Type',
        'epistemic_entropy': 'Epistemic Entropy',
        'knightian_kelly': 'Knightian Kelly'
    })
    
    display_df = top_10[['Market Name', 'Market Price', 'De-Biased Price', 'Alpha %', 'Bias Type', 'Epistemic Entropy', 'Knightian Kelly', 'Trade Rating']].copy()
    
    display_df['Market Price'] = display_df['Market Price'].apply(lambda x: f"${x:.3f}")
    display_df['De-Biased Price'] = display_df['De-Biased Price'].apply(lambda x: f"${x:.4f}")
    display_df['Alpha %'] = display_df['Alpha %'].apply(lambda x: f"{x:.2%}")
    #display_df['Epistemic Entropy'] = display_df['Epistemic Entropy'].apply(lambda x: f"{x:.3f}")
    #display_df['Knightian Kelly'] = display_df['Knightian Kelly'].apply(lambda x: f"{x:.2%}")
    display_df['Market Name'] = display_df['Market Name'].apply(lambda x: (x[:35] + '...') if isinstance(x, str) and len(x) > 38 else x)
    
    table = tabulate(display_df, headers='keys', tablefmt='simple', showindex=False)
    print(table)
    
    print("-" * 130)
    print(f"Average Market Cognitive Friction: {market_rationality_score:.2f}%")
    
    csv_file = "signals_log.csv"
    save_cols = ['Timestamp', 'Market Name', 'Market Price', 'De-Biased Price', 'Alpha %', 'Bias Type']#, 'Epistemic Entropy', 'Knightian Kelly', 'Trade Rating']
    top_10[save_cols].to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession terminated.")
