from core import yf, FSAccessor
import logging

"""

Asset Turnover = Revenue / Average Total Assets

Inventory Turnover = Cost of Revenue / Average Inventory

Receivables Turnover = Revenue / Average Accounts Receivable

These measure how well assets are being used.

"""
class Efficiency:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def asset_turnover(self) -> float | None:
        revenue_series = self.fs.get_metric("Total Revenue")
        assets_series = self.fs.get_metric("Total Assets")

        if revenue_series is None or assets_series is None:
            return None # FSAccessor already logged the reason.

        try:
            total_revenue = self.fs.latest(revenue_series)
            curr_assets, prev_assets = self.fs.latest_and_prev(assets_series)
            
            avg_assets = (curr_assets + prev_assets) / 2
            if avg_assets == 0:
                return 0.0
            return total_revenue / avg_assets
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Asset Turnover due to insufficient data: {e}")
            return None
    
    def inventory_turnover(self) -> float | None:
        cogs_series = self.fs.get_metric("Cost Of Revenue") 
        inventory_series = self.fs.get_metric("Inventory")

        if cogs_series is None or inventory_series is None:
            return None

        try:
            cost_of_revenue = self.fs.latest(cogs_series)
            curr_inventory, prev_inventory = self.fs.latest_and_prev(inventory_series)

            avg_inventory = (curr_inventory + prev_inventory) / 2
            if avg_inventory == 0:
                return 0.0
            return cost_of_revenue / avg_inventory
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Inventory Turnover due to insufficient data: {e}")
            return None

    def receivables_turnover(self) -> float | None:
        revenue_series = self.fs.get_metric("Total Revenue")
        ar_series = self.fs.get_metric("Accounts Receivable")

        if revenue_series is None or ar_series is None:
            return None

        try:
            total_revenue = self.fs.latest(revenue_series)
            curr_ar, prev_ar = self.fs.latest_and_prev(ar_series)
            
            avg_ar = (curr_ar + prev_ar) / 2
            if avg_ar == 0:
                return 0.0
            return total_revenue / avg_ar
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Receivables Turnover due to insufficient data: {e}")
            return None
