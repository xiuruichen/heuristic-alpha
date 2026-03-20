"""
Cumulative Prospect Theory (CPT) Engine for De-Biasing Prediction Market Prices.

This module provides a mathematical translation of market prices
into 'Fair' statistical probabilities, specifically designed to model the 
Favorite-Longshot Bias.
"""

from typing import Union
import numpy as np
import pandas as pd

class ProspectEngine:
    """
    Cumulative Prospect Theory (CPT) engine for de-biasing prediction market prices.
    """
    
    def prelec_weight(self, p: Union[float, np.ndarray, pd.Series], gamma: float = 0.61) -> Union[float, np.ndarray, pd.Series]:
        """Calculates the Prelec Probability Weighting Function."""
        p_clipped: Union[float, np.ndarray, pd.Series] = np.clip(p, 1e-9, 1.0 - 1e-9)
        return np.exp(-(-np.log(p_clipped))**gamma)

    def tversky_kahneman_value(self, x: Union[float, np.ndarray, pd.Series], alpha: float = 0.88, beta: float = 0.88, lambda_: float = 2.25) -> Union[float, np.ndarray]:
        """Calculates the Tversky-Kahneman Value Function for loss aversion."""
        x_array: np.ndarray = np.asarray(x, dtype=float)
        
        if x_array.ndim == 0:
            if x_array >= 0:
                return float(x_array**alpha)
            else:
                return float(-lambda_ * (-x_array)**beta)
                
        result: np.ndarray = np.zeros_like(x_array)
        pos_mask: np.ndarray = x_array >= 0
        neg_mask: np.ndarray = x_array < 0
        
        result[pos_mask] = x_array[pos_mask]**alpha
        result[neg_mask] = -lambda_ * (-x_array[neg_mask])**beta
        
        return result

    def get_fair_probability(self, market_price: Union[float, np.ndarray, pd.Series], gamma: float = 0.61) -> Union[float, np.ndarray, pd.Series]:
        """
        Translates a market price into a 'Fair' objective probability.
        Mathematically, w(p) is clipped to (0.0, 1.0) exclusive to avoid 
        math domain errors during logarithmic evaluations.
        """
        w_p: Union[float, np.ndarray, pd.Series] = np.clip(market_price, 1e-9, 1.0 - 1e-9)
        return np.exp(-(-np.log(w_p))**(1.0 / gamma))

    def confidence_interval(self, market_price: Union[float, np.ndarray, pd.Series], gamma: float = 0.61, shift: float = 0.05) -> tuple:
        """Calculates parameter-sensitive confidence bounds for the Fair Probability."""
        lower_gamma = gamma - shift
        upper_gamma = gamma + shift
        
        prob_gamma_low = self.get_fair_probability(market_price, gamma=lower_gamma)
        prob_gamma_high = self.get_fair_probability(market_price, gamma=upper_gamma)
        
        return (np.minimum(prob_gamma_low, prob_gamma_high), 
                np.maximum(prob_gamma_low, prob_gamma_high))

    def calculate_market_rationality(self, alpha_series: pd.Series) -> float:
        """
        Calculates the average Alpha Edge across the provided market series.
        A high score indicates widespread inefficiency.
        """
        if alpha_series.empty:
            return 0.0
        return float(alpha_series.mean() * 100.0)

    def calculate_shannon_entropy(self, p: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
        """Calculates the Shannon Entropy to measure the market's ambiguity."""
        p_safe = np.clip(p, 1e-9, 1.0 - 1e-9)
        entropy = -p_safe * np.log2(p_safe) - (1.0 - p_safe) * np.log2(1.0 - p_safe)
        return entropy

    def calculate_ergodic_kelly(self, p_fair: Union[float, np.ndarray, pd.Series], p_market: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
        """Evaluates the optimal capital allocation satisfying the Kelly Criterion."""
        p_market_safe = np.clip(p_market, 1e-9, 1.0 - 1e-9)
        b = (1.0 / p_market_safe) - 1.0
        
        q_fair = 1.0 - p_fair
        f_star = p_fair - (q_fair / b)
        
        return np.maximum(0.0, f_star)
