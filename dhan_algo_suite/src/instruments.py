import pandas as pd
from pathlib import Path

# Load Dhan Instrument List CSV exported from Dhan docs (Annexure).
# Must include columns like: securityId, tradingSymbol, exchangeSegment, instrument, drvStrikePrice, drvOptionType, drvExpiryDate
def load_instruments(csv_path: str | Path = "data/instruments.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # normalize columns
    df.columns = [c.strip() for c in df.columns]
    return df

def find_atm_option(df: pd.DataFrame, underlying_ltp: float, expiry: str, option_type: str, 
                    exchange_segment: str = "IDX_I", tick: int = 50):
    # For NIFTY index options with 50/100 strike steps (adjust tick as needed).
    # Choose ATM (nearest strike) or slightly ITM: prefer ATM; if ITM requested, shift one tick into ITM.
    strikes = df[(df["exchangeSegment"] == exchange_segment) & (df["drvExpiryDate"] == expiry)]
    strikes = strikes[strikes["drvOptionType"].str.upper().isin(["CALL","PUT"])]
    # Round to nearest strike increment
    nearest = round(underlying_ltp / tick) * tick
    if option_type.upper() == "CALL":
        atm = nearest
    else:
        atm = nearest
    # choose closest available
    chosen = strikes.loc[(strikes["drvStrikePrice"]-atm).abs().sort_values().index].head(1)
    if chosen.empty:
        raise ValueError("No ATM strike found for filters")
    return chosen.iloc[0].to_dict()
