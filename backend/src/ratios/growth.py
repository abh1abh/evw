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
        try:
            revenue_rows = self.fs.get_row(self.fs.income, ["Total Revenue"])
            curr_revenue, prev_revenue = self.fs.latest_and_prev(revenue_rows)
            if prev_revenue == 0:
                return 0.0
            return (curr_revenue - prev_revenue) / prev_revenue
        except Exception:
            logging.exception("Error Calculating Revenue Growth")
            return None
        
    def net_income_growth(self) -> float | None:
        try:
            ni_rows = self.fs.get_row(self.fs.income, ["Net Income"])
            curr_ni, prev_ni = self.fs.latest_and_prev(ni_rows)
            if prev_ni == 0:
                return 0.0
            return (curr_ni - prev_ni) / prev_ni
        except Exception:
            logging.exception("Error Calculating Net Income Growth")
            return None
    
    def eps_growth(self) -> float | None:
        try:
            eps_rows = self.fs.get_row(self.fs.income, ["Diluted EPS", "Basic EPS"])
            curr_eps, prev_eps = self.fs.latest_and_prev(eps_rows)
            if prev_eps is None or prev_eps <= 0:
                return None
            return (curr_eps - prev_eps) / prev_eps
        except Exception:
            logging.exception("Error Calculating Earning Per Share Growth")
            return None
        