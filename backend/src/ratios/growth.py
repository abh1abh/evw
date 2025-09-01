from core import yf, FSAccessor
import logging

"""
Revenue Growth = (Revenue this year - Revenue last year) / Revenue last year

Net Income Growth = (Net Income this year - last year) / last year

EPS Growth = (EPS this year - last year) / last year

Growth rates show trends over time.

"""

class Growth:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def revenue_growth(self) -> float | None:
        revenue_series = self.fs.get_metric("Total Revenue")
        if revenue_series is None:
            return None

        try:
            curr_revenue, prev_revenue = self.fs.latest_and_prev(revenue_series)
            if prev_revenue == 0:
                return 0.0
            return (curr_revenue - prev_revenue) / prev_revenue
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Revenue Growth due to insufficient data: {e}")
            return None
        
    def net_income_growth(self) -> float | None:
        ni_series = self.fs.get_metric("Net Income")
        if ni_series is None:
            return None

        try:
            curr_ni, prev_ni = self.fs.latest_and_prev(ni_series)
            if prev_ni == 0:
                return 0.0
            return (curr_ni - prev_ni) / prev_ni
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Net Income Growth due to insufficient data: {e}")
            return None
    
    def eps_growth(self) -> float | None:
        eps_series = self.fs.get_metric("Diluted EPS")
        if eps_series is None:
            return None

        try:
            curr_eps, prev_eps = self.fs.latest_and_prev(eps_series)
            if prev_eps is None or prev_eps == 0:
                return 0.0
            return (curr_eps - prev_eps) / prev_eps
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate EPS Growth due to insufficient data: {e}")
            return None
        