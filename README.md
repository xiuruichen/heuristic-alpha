# Heuristic Alpha

Heuristic Alpha is a computational pipeline designed to quantify and exploit the *Favorite-Longshot Bias* in decentralized prediction markets like Polymarket. 

By unifying **Behavioral Economics, Quantitative Finance (Statistical Mechanics), and Information Theory**, this project explores the cognitive boundaries of human irrationality and pricing inefficiencies. It algorithmically flags predictable mispricings where humans either under-weight probable events or over-weight extreme lottery-like longshots.

## Theoretical Basis

### 1. Cumulative Prospect Theory (Neuroeconomics)
At the core of Heuristic Alpha is the mathematical translation of market point-prices via the **Tversky & Kahneman Cumulative Prospect Theory**. The algorithm calculates objective 'Fair' mathematical probabilities by applying the inverse of the **Prelec Probability Weighting Function**.

### 2. Epistemic Entropy (Information Theory)
The engine measures fundamental market ambiguity by calculating the **Shannon Entropy** ($H(p)$) of point distributions. Markets floating near a 50/50 probability contain maximum entropy, identifying locations where ambiguity aversion (the Ellsberg Paradox) artificially distorts capital flow.

### 3. Ergodicity Economics & Knightian Allocation
The strategy departs from classical ensemble-average risk frameworks to natively calculate time-average compound growth allocations via the **Kelly Criterion**. Using the **Knightian Penalty**, the algorithm algorithmically discounts Kelly bet sizing inversely to the surrounding Shannon Entropy—safely hedging against purely ambiguous noise.

## Codebase Architecture

To navigate this project, understand the three critical pillars logic lives in:

1. **`src/core/cognitive.py`**
   - **`Prospect`**: The math brain. It holds the vectorized Numpy calculations for Prelec Probability Weightings, the Tversky-Kahneman Value functions, Shannon Entropy limits, and the statistical Ergodic Kelly constraints. 
   - *Where to look:* `get_fair_probability()` is the heart of the De-Biasing math.

2. **`src/data/fetcher.py`**
   - **`Fetcher`**: The sensory pipeline using asynchronous `aiohttp` looping. It pulls raw CLOB data globally, parsing through bid-ask spreads to calculate True Midpoint prices and immediately filtering out "dust" liquidity (<$500) markets.

3. **`src/strategy/engine.py`**
   - **`Engine`**: The bridge. It takes the clean DataFrame from the fetcher, feeds it through the `ProspectEngine`, and assigns psychological tagging (`Bias Type`) and our composite scoring metrics (`Knightian Kelly` & `Signal Strength`).

4. **`main.py`**
   - The primary execution driver. Connects the API, initiates the loop, handles 429 Rate Limits, renders the CLI terminal ASCII dashboard, and appends outputs historically to `signals_log.csv`.
   
5. **`tests/math_check.py`**
   - Isolated environment to run a static `Dummy Market` check preventing mathematical drift during future updates.

## Disclaimer 

**For Research Purposes Only.** 
This pipeline is an academic exploration of decision-making algorithms and behavioral finance. It firmly does NOT constitute financial advice. Prediction markets are volatile, and users utilize this repository's models strictly at their own risk. Code should be carefully reviewed regarding authorization and execution boundaries.
