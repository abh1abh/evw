
from core import yf, FSAccessor
import logging

class Leverage:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)
    
    def debt_to_equity(self) -> float | None:
        debt_series = self.fs.get_metric("Total Debt")
        equity_series = self.fs.get_metric("Stockholders Equity")

        if debt_series is None or equity_series is None:
            return None

        try:
            total_debt = self.fs.latest(debt_series)
            equity = self.fs.latest(equity_series)
            if equity == 0:
                return 0.0
            return total_debt / equity
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Debt to Equity due to insufficient data: {e}")
            return None
    
    def debt_ratio(self) -> float | None:
        debt_series = self.fs.get_metric("Total Debt")
        assets_series = self.fs.get_metric("Total Assets")

        if debt_series is None or assets_series is None:
            return None

        try:
            total_debt = self.fs.latest(debt_series)
            total_assets = self.fs.latest(assets_series)
            if total_assets == 0:
                return 0.0
            return total_debt / total_assets
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Debt Ratio due to insufficient data: {e}")
            return None

    def equity_ratio(self) -> float | None:
        equity_series = self.fs.get_metric("Stockholders Equity")
        assets_series = self.fs.get_metric("Total Assets")

        if equity_series is None or assets_series is None:
            return None

        try:
            total_equity = self.fs.latest(equity_series)
            total_assets = self.fs.latest(assets_series)
            if total_assets == 0:
                return 0.0
            return total_equity / total_assets
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Equity Ratio due to insufficient data: {e}")
            return None

    def interest_coverage(self) -> float | None:
        interest_series = self.fs.get_metric("Interest Expense")
        ebit_series = self.fs.get_metric("EBIT")

        if interest_series is None or ebit_series is None:
            return None

        try:
            interest_expense = self.fs.latest(interest_series)
            ebit = self.fs.latest(ebit_series)
            if interest_expense == 0:
                return float('inf') # Or a large number to signify high coverage
            return ebit / interest_expense
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Interest Coverage due to insufficient data: {e}")
            return None
