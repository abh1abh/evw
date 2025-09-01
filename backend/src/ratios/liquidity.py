from core import yf, FSAccessor
import logging

"""
Liquidity Ratios

Current Ratio = Current Assets / Current Liabilities

Quick Ratio = (Current Assets - Inventory) / Current Liabilities

These test short-term financial health (ability to pay obligations).

"""

class Liquidity:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def current_ratio(self) -> float | None:
        assets_series = self.fs.get_metric("Current Assets")
        liabilities_series = self.fs.get_metric("Current Liabilities")

        if assets_series is None or liabilities_series is None:
            return None

        try:
            assets = self.fs.latest(assets_series)
            liabilities = self.fs.latest(liabilities_series)
            if liabilities == 0:
                return 0.0
            return assets / liabilities
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Current Ratio due to insufficient data: {e}")
            return None
        
    def quick_ratio(self) -> float | None:
        assets_series = self.fs.get_metric("Current Assets")
        liabilities_series = self.fs.get_metric("Current Liabilities")
        inventory_series = self.fs.get_metric("Inventory")

        if assets_series is None or liabilities_series is None or inventory_series is None:
            return None

        try:
            assets = self.fs.latest(assets_series)
            liabilities = self.fs.latest(liabilities_series)
            inventory = self.fs.latest(inventory_series)
            if liabilities == 0:
                return 0.0
            return (assets - inventory) / liabilities
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Quick Ratio due to insufficient data: {e}")
            return None
        