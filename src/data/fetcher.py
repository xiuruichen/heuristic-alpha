"""
Polymarket CLOB Data Pipeline.

Asynchronously fetches live market data from the Polymarket API 
and filters down to tradable opportunities.
"""

import asyncio
import aiohttp
import pandas as pd
from typing import List, Dict, Any, Optional

import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class PolymarketFetcher:
    """
    Fetches market conditions, pricing, and volume data.
    """
    
    API_BASE: str = "https://clob.polymarket.com"
    
    def __init__(self) -> None:
        pass
        
    async def fetch_markets(self) -> pd.DataFrame:
        """
        Retrieves active markets.
        Filters out markets with 'dust' liquidity (less than $500).
        """
        markets: List[Dict[str, Any]] = []
        next_cursor: str = ""
        
        async with aiohttp.ClientSession() as session:
            while True:
                url = f"{self.API_BASE}/markets"
                if next_cursor:
                    url += f"?next_cursor={next_cursor}"
                
                async with session.get(url) as response:
                    if response.status == 429:
                        print("Rate limit (429) hit. Cooling down for 60 seconds...")
                        await asyncio.sleep(60)
                        continue
                        
                    if response.status != 200:
                        print(f"Failed to fetch from {url}, status code: {response.status}")
                        break
                        
                    data = await response.json()
                    page_markets = data.get("data", [])
                    
                    if not page_markets:
                        break
                        
                    for m in page_markets:
                        if not m.get("active", False) or m.get("closed", False):
                            continue
                            
                        tokens = m.get("tokens", [])
                        yes_price: Optional[float] = None
                        
                        for token in tokens:
                            if str(token.get("outcome", "")).lower() == "yes":
                                best_bid = float(token.get("best_bid", token.get("price", 0.0)))
                                best_ask = float(token.get("best_ask", token.get("price", 0.0)))
                                yes_price = (best_bid + best_ask) / 2.0
                                break
                                
                        if yes_price is None and "price" in m:
                            best_bid = float(m.get("best_bid", m.get("price", 0.0)))
                            best_ask = float(m.get("best_ask", m.get("price", 0.0)))
                            yes_price = (best_bid + best_ask) / 2.0
                        elif yes_price is None and len(tokens) > 0:
                            yes_price = float(tokens[0].get("price", 0.0))
                            
                        try:
                            volume: float = float(m.get("volume", 1000.0))
                        except (ValueError, TypeError):
                            volume = 1000.0
                            
                        try:
                            liquidity: float = float(m.get("liquidity", 1000.0))
                        except (ValueError, TypeError):
                            liquidity = 1000.0
                            
                        if yes_price is not None:
                            markets.append({
                                "condition_id": m.get("condition_id"),
                                "question": m.get("question", "Unknown"),
                                "current_price": yes_price,
                                "volume": volume,
                                "liquidity": liquidity
                            })
                            
                    next_cursor = data.get("next_cursor", "")
                    if not next_cursor or next_cursor == "LTE=":
                        break
                    
                    if len(markets) > 2000:
                        break

        df = pd.DataFrame(markets)
        if df.empty:
            return pd.DataFrame(columns=["condition_id", "question", "current_price", "volume", "liquidity"])
            
        df['liquidity'] = pd.to_numeric(df['liquidity'], errors='coerce').fillna(1000.0)
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(1000.0)
        
        df['is_liquid'] = df['liquidity'] >= 500.0
        df = df[df['is_liquid']].reset_index(drop=True)
        
        return df
