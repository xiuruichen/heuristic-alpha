"""
Heuristic Alpha Strategy Engine.

Calculates the Alpha Edge, applies the Favorite-Longshot Filter,
and ranks tradable signals using the Cognitive Engine's theoretical models.
"""

import numpy as np
import pandas as pd
from typing import Optional

from src.core.cognitive import ProspectEngine

class AlphaEngine:
    """
    Engine to detect mispricings resulting from Favorite-Longshot Bias.
    """
    
    def __init__(self) -> None:
        self.prospect_engine = ProspectEngine()
        
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyzes a DataFrame of markets, calculating fair probabilities and edges.
        """
        if df.empty:
            return df
            
        df['fair_probability'] = self.prospect_engine.get_fair_probability(df['current_price'])
        
        df['spread'] = df['current_price'] - df['fair_probability']
        df['alpha_edge'] = df['spread'] / np.clip(df['fair_probability'], 1e-9, None)
        
        safe_liquidity = np.clip(df['liquidity'], 1.0, None)
        df['friction_score'] = df['volume'] / safe_liquidity
        
        df['epistemic_entropy'] = self.prospect_engine.calculate_shannon_entropy(df['current_price'])
        
        def get_bias_type(row):
            if row['current_price'] < 0.15 and row['alpha_edge'] > 1.0:
                return "Lottery Overweighting"
            elif row['current_price'] > 0.85 and row['alpha_edge'] < 0.0:
                return "Certainty Bias"
            return "Proportional"
            
        df['bias_type'] = df.apply(get_bias_type, axis=1)
        
        df['kelly_fraction'] = self.prospect_engine.calculate_ergodic_kelly(df['fair_probability'], df['current_price'])
        df['knightian_kelly'] = df['kelly_fraction'] * (1.0 - df['epistemic_entropy'])
        
        # Filter for positive edge within standard deviation boundaries
        condition_filter = (
            (df['current_price'] >= 0.02) & 
            (df['current_price'] <= 0.15) & 
            (df['alpha_edge'] > 0)
        )
        
        df_filtered = df[condition_filter].copy()
        
        if df_filtered.empty:
            return df_filtered
            
        df_filtered['signal_strength'] = df_filtered['alpha_edge'] * np.log1p(df_filtered['friction_score'])
        
        df_ranked = df_filtered.sort_values(by='signal_strength', ascending=False).reset_index(drop=True)
        return df_ranked
