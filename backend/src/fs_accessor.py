import yfinance as yf
from functools import lru_cache
import pandas as pd
from typing import Iterable, Tuple
from dataclasses import dataclass

@dataclass
class FSAccessor:
    ticker: yf.Ticker

    @property
    def income(self) -> pd.DataFrame:
        df = self.ticker.financials.copy()
        return self._sort_columns(df)

    @property
    def balance(self) -> pd.DataFrame:
        df = self.ticker.balance_sheet.copy()
        return self._sort_columns(df)
    
    @staticmethod
    def _sort_columns(df: pd.DataFrame) -> pd.DataFrame:
        # yfinance columns are datelike strings; coerce to datetime and sort desc
        cols = pd.to_datetime(df.columns, errors="coerce")
        order = pd.Series(range(len(cols)), index=df.columns)
        if cols.notna().all():
            order = pd.Series(cols, index=df.columns).sort_values(ascending=False)
            return df.loc[:, order.index]
        return df  # fallback: leave as-is

    def get_row(self, df: pd.DataFrame, keys: Iterable[str]) -> pd.Series:
        for k in keys:
            if k in df.index:
                return df.loc[k]
        raise KeyError(f"None of the keys found: {list(keys)}\nAvailable rows: {df.index.tolist()}")


    def latest_and_prev(self, row: pd.Series) -> Tuple[float, float]:
        # Ensure we have at least 2 columns
        vals = row.dropna().astype(float)
        if len(vals) < 2:
            raise ValueError(f"Need at least two periods for average. Got: {vals.to_dict()}")
        return float(vals.iloc[0]), float(vals.iloc[1])