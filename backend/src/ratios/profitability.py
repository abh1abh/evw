from core import yf, FSAccessor
import logging

class Profitability:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def net_margin(self) -> float | None:
        ni_series = self.fs.get_metric("Net Income")
        revenue_series = self.fs.get_metric("Total Revenue")

        if ni_series is None or revenue_series is None:
            return None

        try:
            ni = self.fs.latest(ni_series)
            rev = self.fs.latest(revenue_series)
            if rev == 0:
                return 0.0
            return ni / rev
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Net Margin due to insufficient data: {e}")
            return None
        
    def gross_profit_margin(self) -> float | None:
        gp_series = self.fs.get_metric("Gross Profit")
        revenue_series = self.fs.get_metric("Total Revenue")

        if gp_series is None or revenue_series is None:
            return None

        try:
            gp = self.fs.latest(gp_series)
            rev = self.fs.latest(revenue_series)
            if rev == 0:
                return 0.0
            return gp / rev
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Gross Profit Margin due to insufficient data: {e}")
            return None
    
    def operating_margin(self) -> float | None:
        op_income_series = self.fs.get_metric("Operating Income")
        revenue_series = self.fs.get_metric("Total Revenue")

        if op_income_series is None or revenue_series is None:
            return None

        try:
            op_income = self.fs.latest(op_income_series)
            rev = self.fs.latest(revenue_series)
            if rev == 0:
                return 0.0
            return op_income / rev
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Operating Margin due to insufficient data: {e}")
            return None
        
    def ebitda_margin(self) -> float | None:
        ebitda_series = self.fs.get_metric("EBITDA")
        revenue_series = self.fs.get_metric("Total Revenue")

        if ebitda_series is None or revenue_series is None:
            return None

        try:
            ebitda = self.fs.latest(ebitda_series)
            rev = self.fs.latest(revenue_series)
            if rev == 0:
                return 0.0
            return ebitda / rev
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate EBITDA Margin due to insufficient data: {e}")
            return None

    def roa(self) -> float | None:
        ni_series = self.fs.get_metric("Net Income")
        assets_series = self.fs.get_metric("Total Assets")

        if ni_series is None or assets_series is None:
            return None

        try:
            ni = self.fs.latest(ni_series)
            curr_assets, prev_assets = self.fs.latest_and_prev(assets_series)
            avg_assets = (curr_assets + prev_assets) / 2
            if avg_assets == 0:
                return 0.0
            return ni / avg_assets
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate ROA due to insufficient data: {e}")
            return None
        
    def roe(self) -> float | None:
        ni_series = self.fs.get_metric("Net Income")
        equity_series = self.fs.get_metric("Stockholders Equity")

        if ni_series is None or equity_series is None:
            return None

        try:
            ni = self.fs.latest(ni_series)
            eq_curr, eq_prev = self.fs.latest_and_prev(equity_series)
            avg_eq = (eq_curr + eq_prev) / 2.0
            if avg_eq == 0:
                return 0.0
            return ni / avg_eq
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate ROE due to insufficient data: {e}")
            return None
