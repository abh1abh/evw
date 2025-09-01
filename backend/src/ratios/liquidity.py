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

    def _get_assets(self):
        return self.fs.latest(self.fs.get_row(self.fs.balance, ["Current Assets"]))

    def _get_liabilities(self):
        return self.fs.latest(self.fs.get_row(self.fs.balance, ["Current Liabilities"]))
    
    def _get_inventory(self):
        return self.fs.latest(self.fs.get_row(self.fs.balance, ["Inventory"]))

    def current_ratio(self) -> float | None:
        try:
            assets = self._get_assets()
            liabilities = self._get_liabilities()
            if liabilities == 0:
                return 0.0
            return assets / liabilities
        except Exception:
            logging.exception("Error Calculating Current ratio")
            return None
        
    def quick_ratio(self) -> float | None:
        try:
            assets = self._get_assets()
            liabilities = self._get_liabilities()
            inventory = self._get_inventory()
            if liabilities == 0:
                return 0.0
            return (assets - inventory) / liabilities
        except Exception:
            logging.exception("Error Calculating Quick ratio")
            return None
        