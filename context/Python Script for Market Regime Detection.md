
A Python script for Google that performs market regime detection on the S&P 500 using a hidden Markov model (HMM). Requirements:

1. Install libraries: `yfinance`, `hmmlearn`, `matplotlib, `pandas`, `numpy`, `scikit-learn` 
2. Get Data: - Download hourly market data for the last 730 days using yfinance. - Important column: use YF.download with.equals to 730d and interval equals 1H (do not use start-end dates). - After downloading, handle yfinance multi index columns so the final columns are exactly: open, high, low, close, volume (if columns are multi-indexed, flattened using get_level_values(0), not the last level) - ensure the script does not throw a key error on open/high/low/close/volume. 
3. Feature engineering: create exactly these 3 features: - Returns = Close.pct_change() - Range = (High - Low) / Close - Vol_Change = Volume.pct_change() Then clean the data by dropping NaNs and also replacing inf/*inf with NaN and dropping again. 
4) Train model: - initialize HMMlearn.HMM.GaussianHMM with: N_components=7, covariance_type=4, N_ITR=1000, random_state=42 - fit it on X=data[returns, range, vol_change]].values. - Predict the hidden states and store them in data[State], 
5) Analyze: Print a summary table with one row per state showing: mean_Return (Mean of returns) Volatility (STD of returns) Count (Number of samples) Sort the table by Mean_Return descending. 
6. Plot the S&P500 closed price for the last 500 hours. - Overlay a scatter plot of the closed prices with dots colored by the detected state (7 regimes). - Use a distinct color map and include a legend.
