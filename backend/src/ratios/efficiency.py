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

    def _get_revenue_rows(self):
        return self.fs.get_row(self.fs.income, ["Total Revenue"])
        
    def asset_turnover(self) -> float | None:
        try:
            total_revenue = self.fs.latest(self._get_revenue_rows())
            total_assets_rows = self.fs.get_row(self.fs.balance, ["Total Assets"])
            curr_assets, prev_assets = self.fs.latest_and_prev(total_assets_rows)
            avg_assets = (curr_assets + prev_assets) / 2
            if avg_assets == 0:
                return 0.0
            return total_revenue / avg_assets
        except Exception:
            logging.exception("Failed to Calculate Asset Turnover")
            return None
    
    def inventory_turnover(self) -> float | None:
        try:
            cost_of_revenue_rows = self.fs.get_row(self.fs.income, ["Cost Of Revenue"]) 
            cost_of_revenue = self.fs.latest(cost_of_revenue_rows)
            inventory_rows = self.fs.get_row(self.fs.balance, ["Inventory"])
            curr_inventory, prev_inventory = self.fs.latest_and_prev(inventory_rows)
            avg_inventory = (curr_inventory + prev_inventory) / 2
            if avg_inventory == 0:
                return 0.0
            return cost_of_revenue / avg_inventory
        except Exception:
            logging.exception("Failed to Calculate Inventory Turnover")
            return None

    def receivables_turnover(self) -> float | None:
        try:
            total_revenue = self.fs.latest(self._get_revenue_rows())
            ar_rows = self.fs.get_row(self.fs.balance, ["Accounts Receivable"])
            curr_ar, prev_ar = self.fs.latest_and_prev(ar_rows)
            avg_ar = (curr_ar + prev_ar) / 2
            if avg_ar == 0:
                return 0.0
            return total_revenue / avg_ar
        except Exception:
            logging.exception("Failed to Calculate Receivables Turnover")
            return None