from core import yf, FSAccessor

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

    
    def current_ratio(self) -> float:
        try:
            assets = self._get_assets()
            liabilities = self._get_liabilities()
            if liabilities == 0:
                raise ValueError("Current Liabilities is zero; ratio undefined.")
            return assets / liabilities
        
        except Exception as e:
            raise RuntimeError(f"Error Calculating Current ratio: {e}")
        
    def quick_ratio(self) -> float:
        try:
            assets = self._get_assets()
            liabilities = self._get_liabilities()
            inventory = self._get_inventory()
            if liabilities == 0:
                raise ValueError("Current Liabilities is zero; ratio undefined.")
            return (assets - inventory) / liabilities
        except Exception as e:
            raise RuntimeError(f"Error Calculating Current ratio: {e}")
        