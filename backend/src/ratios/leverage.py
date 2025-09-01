
from core import yf, FSAccessor
import logging

class Leverage:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def _get_equity_rows(self):
        return self.fs.get_row(
            self.fs.balance,
            ["Common Stock Equity", "Stockholders Equity", "Total Stockholder Equity"]
        )

    def _get_total_debt_rows(self):
        return self.fs.get_row(self.fs.balance, ["Total Debt"])
    
    def _get_total_assets_rows(self):
        return self.fs.get_row(self.fs.balance, ["Total Assets"])
    
    def debt_to_equity(self) -> float | None:
        try:
            total_debt = self.fs.latest(self._get_total_debt_rows())
            equity = self.fs.latest(self._get_equity_rows())
            if equity == 0:
                return 0.0
            return total_debt / equity
        except Exception:
            logging.exception("Error Calculation Debt to Equity")
            return None
    
    def debt_ratio(self) -> float | None:
        try:
            total_debt = self.fs.latest(self._get_total_debt_rows())
            total_assets = self.fs.latest(self._get_total_assets_rows())
            if total_assets == 0:
                return 0.0
            return total_debt / total_assets
        except Exception:
            logging.exception("Error Calculation Debt Ratio")
            return None

    def equity_ratio(self) -> float | None:
        try:
            total_equity = self.fs.latest(self._get_equity_rows())
            total_assets = self.fs.latest(self._get_total_assets_rows())
            if total_assets == 0:
                return 0.0
            return total_equity / total_assets
        except Exception:
            logging.exception("Error Calculation Equity Ratio")
            return None

    def interest_coverage(self) -> float | None:
        try:
            interest_expense_rows = self.fs.get_row(self.fs.income, ["Interest Expense"])
            ebit_rows = self.fs.get_row(self.fs.income, ["EBIT"])
            interest_expense = self.fs.latest(interest_expense_rows)
            ebit = self.fs.latest(ebit_rows)
            if interest_expense == 0:
                return float('inf') # Or a large number to signify high coverage
            return ebit / interest_expense
        except Exception:
            logging.exception("Error Calculation Interest Coverage")
            return None
