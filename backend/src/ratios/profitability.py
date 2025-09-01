from core import yf, FSAccessor
import logging

class Profitability:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def _revenue(self):
        rev_row = self.fs.get_row(self.fs.income, ["Total Revenue", "Operating Revenue"])
        rev = self.fs.latest(rev_row)
        if rev == 0:
            raise ValueError("Revenue is zero.")
        return rev
    
    def net_margin(self) -> float | None:
        try:
            net_income_row = self.fs.get_row(self.fs.income, ["Net Income", "Net Income Common Stockholders"])
            ni = self.fs.latest(net_income_row)
            rev = self._revenue()
            return ni / rev
        except Exception:
            logging.exception("Failed to compute Net Margin")
            return None
        
    def gross_profit_margin(self) -> float | None:
        try:
            gp_row = self.fs.get_row(self.fs.income, ["Gross Profit"])
            gp = self.fs.latest(gp_row)
            rev = self._revenue()
            return gp / rev
        except Exception:
            logging.exception("Failed to compute Gross Margin")
            return None
    
    def operating_margin(self) -> float | None:
        try:
            op_row = self.fs.get_row(self.fs.income, ["Operating Income", "Total Operating Income As Reported"])
            op  = self.fs.latest(op_row)
            rev = self._revenue()
            return op / rev
        except Exception:
            logging.exception("Failed to compute Operating Margin")
            return None
        
    def ebitda_margin(self) -> float | None:
        try:
            ebitda_row = self.fs.get_row(self.fs.income, ["EBITDA", "Normalized EBITDA"])
            ebitda = self.fs.latest(ebitda_row)
            rev = self._revenue()
            return ebitda / rev
        except Exception:
            logging.exception("Failed to compute EBITDA Margin")
            return None

    def roa(self) -> float | None:
        try:
            net_income_rows = self.fs.get_row(self.fs.income, ["Net Income"])
            ni = self.fs.latest(net_income_rows)

            total_assets_rows = self.fs.get_row(self.fs.balance, ["Total Assets"])
            curr_assets, prev_assets = self.fs.latest_and_prev(total_assets_rows)
            avg_assets = (curr_assets + prev_assets) / 2
            if avg_assets == 0:
                return 0.0
            return ni / avg_assets
        except Exception:
            logging.exception("Failed to compute ROA")
            return None
        
    def roe(self) -> float | None:
        try:
            net_income_row = self.fs.get_row(self.fs.income, ["Net Income", "Net Income Common Stockholders"])
            ni, _ = self.fs.latest_and_prev(net_income_row)
            equity_row = self.fs.get_row(
                self.fs.balance,
                ["Common Stock Equity", "Stockholders Equity", "Total Stockholder Equity"]
            )
            eq_curr, eq_prev = self.fs.latest_and_prev(equity_row)
            avg_eq = (eq_curr + eq_prev) / 2.0
            if avg_eq == 0:
                return 0.0
            return ni / avg_eq
        except Exception:
            logging.exception("Failed to compute ROE")
            return None