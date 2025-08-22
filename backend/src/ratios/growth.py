from core import yf, FSAccessor

"""
Revenue Growth = (Revenue this year - Revenue last year) / Revenue last year

Net Income Growth = (Net Income this year - last year) / last year

EPS Growth = (EPS this year - last year) / last year

Growth rates show trends over time.

"""

class Growth:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def revenue_growth(self) -> float:
        try:
            revenue_rows = self.fs.get_row(self.fs.income, ["Total Revenue"])
            curr_revenue, prev_revenue = self.fs.latest_and_prev(revenue_rows)
            return (curr_revenue - prev_revenue) / prev_revenue
        except Exception as e:
            raise RuntimeError("Error Calculating Revenue Growth: ", e)
        
    def net_income_growth(self) -> float:
        try:
            ni_rows = self.fs.get_row(self.fs.income, ["Net Income"])
            curr_ni, prev_ni = self.fs.latest_and_prev(ni_rows)
            return (curr_ni - prev_ni) / prev_ni
        except Exception as e:
            raise RuntimeError("Error Calculating Net Income Growth: ", e)
    
    def eps_growth(self) -> float:
        try:
            eps_rows = self.fs.get_row(self.fs.income, ["Diluted EPS", "Basic EPS"])
            curr_eps, prev_eps = self.fs.latest_and_prev(eps_rows)
            if prev_eps is None:
                raise ValueError("Previous EPS is missing.")
            if prev_eps == 0:
                raise ValueError("Previous EPS is zero; growth is undefined.")
            if prev_eps < 0:
                raise ValueError("Previous EPS is negative; percentage growth is not meaningful.")
            return (curr_eps - prev_eps) / prev_eps
        except Exception as e:
            raise RuntimeError("Error Calculating Earning Per Share Growth: ", e)
        