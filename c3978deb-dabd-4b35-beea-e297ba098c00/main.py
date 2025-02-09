from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, ATR
# (Other indicators like RSI, etc., could be imported as needed)

class QullamaggieLawsOfSwing(Strategy):
    """
    An example implementation of Qullamaggie’s Laws of Swing.
    
    Key ideas included:
      - Prefer support on a moving average (10-day, then 20-day, then 50-day).
      - Only enter when there is a break of the opening range high (ORH).
      - Avoid entering when the day’s price change exceeds the ATR.
      - Exit (or move stop-loss) when the close falls below the 10-day SMA.
      - Position size is limited (here we simply cap the allocation to 20%).
    
    This is a simplified example. In a production strategy you might include:
      - More dynamic stop-loss calculation (initial stop at the low-of-day, then trailing stops).
      - Partial exits (e.g. take 33%-50% profit after 3 days, then move stop to breakeven).
      - Volume and risk calculations (e.g. “min daily volume > position-size * 200”).
      - Additional entry filters (e.g. avoid buying just before earnings).
    """
    
    @property
    def interval(self) -> str:
        # For this example, we assume a daily strategy.
        return "1d"
    
    @property
    def assets(self) -> list:
        # For demonstration we work with one asset.
        return ["AAPL"]
    
    @property
    def data(self):
        # In many implementations this might be set externally.
        # Here, we assume the framework supplies OHLCV (and possibly other) data.
        pass
    
    def run(self, data: dict) -> TargetAllocation:
        # --- Data Extraction ---
        # Retrieve OHLCV data from the data dictionary.
        # (Expecting a list of dictionaries with keys: open, high, low, close, volume.)
        ohlcv = data.get("ohlcv")
        if not ohlcv or len(ohlcv) < 50:
            # Not enough data to compute a 50-day moving average.
            return TargetAllocation({})
        
        # --- Technical Indicator Calculation ---
        # Compute moving averages (for support levels) and ATR (for risk)
        sma10 = SMA("AAPL", ohlcv, 10)   # 10-day SMA
        sma20 = SMA("AAPL", ohlcv, 20)   # 20-day SMA
        sma50 = SMA("AAPL", ohlcv, 50)   # 50-day SMA
        atr14 = ATR("AAPL", ohlcv, 14)   # 14-day ATR (for stop-loss and volatility filter)
        
        # --- Get Latest OHLCV Data ---
        latest = ohlcv[-1]
        current_open  = latest.get("open")
        current_high  = latest.get("high")
        current_low   = latest.get("low")
        current_close = latest.get("close")
        current_volume = latest.get("volume")
        
        # Log computed indicators for debugging
        log(f"10-day SMA: {sma10[-1]:.2f}, 20-day SMA: {sma20[-1]:.2f}, 50-day SMA: {sma50[-1]:.2f}")
        log(f"ATR (14-day): {atr14[-1]:.2f}")
        
        # --- Entry Conditions ---
        # 1. **Opening Range High (ORH)**
        #    In a full implementation the ORH might be the high of the first candle.
        #    For simplicity, we assume the day's open is our OR reference.
        orh = current_open  # (Replace with a more refined OR calculation if available.)
        
        # 2. **Price Breakout & Support on MAs**
        #    We require that the current close is above the opening range high,
        #    and that it is “near” one of the key moving averages.
        entry_signal = False
        if current_close > orh:
            # For a swing trader, a breakout of the ORH is a candidate entry.
            entry_signal = True
        
        # 3. **Volatility Filter (Avoid if day’s move > ATR)**
        #    If the price-change (close - open) is larger than the ATR,
        #    the move may be too volatile for a clean entry.
        if (current_close - current_open) > atr14[-1]:
            log("Avoiding entry: Price change exceeds ATR.")
            entry_signal = False
        
        # 4. **Moving Average Proximity**
        #    According to Qullamaggie, the strongest setups are when price finds support near a MA.
        #    We define “near” as within 1% of the MA.
        near_sma10 = abs(current_close - sma10[-1]) / sma10[-1] < 0.01
        near_sma20 = abs(current_close - sma20[-1]) / sma20[-1] < 0.01
        near_sma50 = abs(current_close - sma50[-1]) / sma50[-1] < 0.01
        
        if entry_signal:
            if near_sma10:
                log("Entry setup: Price is near the 10-day SMA (strong support).")
            elif near_sma20:
                log("Entry setup: Price is near the 20-day SMA (moderate support).")
            elif near_sma50:
                log("Entry setup: Price is near the 50-day SMA (slower setup).")
            else:
                log("Entry signal present but price is not close enough to a key MA.")
                entry_signal = False  # Do not enter if none of the support levels are near
        
        # --- Position Sizing ---
        # “Don't put more than 20% of your account into any one share.”
        # For this example we simply return an allocation percentage.
        allocation = 0.2 if entry_signal else 0.0
        
        # --- Exit / Stop Conditions ---
        # A key rule is to exit (or move stop-loss) when the price closes below the 10-day SMA.
        if current_close < sma10[-1]:
            log("Exit signal: Price closed below the 10-day SMA.")
            allocation = 0.0

        # (In a more advanced strategy you might also calculate:
        #   - A stop-loss level at the low of day (or adjusted by ATR)
        #   - A profit target after 3 days and then trail your stop using the 10-day SMA.)
        # For example:
        stop_loss = current_low  # initial stop-loss based on the low of the day
        log(f"Stop-loss set at: {stop_loss:.2f}")
        
        # --- Final Allocation ---
        allocation_dict = {"AAPL": allocation}
        return TargetAllocation(allocation_dict)

# A helper logging function (if not provided by your environment)
def log(message: str):
    print(message)