from core import yf, FSAccessor

class Profitability:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def _revenue(self):
        rev_row = self.fs.get_row(self.fs.income, ["Total Revenue", "Operating Revenue"])
        rev = self.fs.latest(rev_row)
        if rev == 0:
            raise ValueError("Revenue is zero.")
        return rev
    
    def net_margin(self):
        try:
            net_income_row = self.fs.get_row(self.fs.income, ["Net Income", "Net Income Common Stockholders"])
            ni = self.fs.latest(net_income_row)
            rev = self._revenue()
            return ni / rev
        except Exception as e:
            raise RuntimeError(f"Failed to compute Net Margin: {e}") from e
        
    def gross_profit_margin(self):
        try:
            gp_row = self.fs.get_row(self.fs.income, ["Gross Profit"])
            gp = self.fs.latest(gp_row)
            rev = self._revenue()
            return gp / rev
        except Exception as e:
            raise RuntimeError(f"Failed to compute Gross Margin:{e} ") from e
    
    def operating_margin(self):
        try:
            op_row = self.fs.get_row(self.fs.income, ["Operating Income", "Total Operating Income As Reported"])
            op  = self.fs.latest(op_row)
            rev = self._revenue()
            return op / rev
        except Exception as e:
            raise RuntimeError(f"Failed to compute Operating Margin: {e}") from e
        
    def ebitda_margin(self):
        try:
            ebitda_row = self.fs.get_row(self.fs.income, ["EBITDA", "Normalized EBITDA"])
            ebitda = self.fs.latest(ebitda_row)
            rev = self._revenue()
            return ebitda / rev
        except Exception as e:
            raise RuntimeError(f"Failed to compute EBITDA Margin: {e}") from e
        

    def roa(self):
        try:
            net_income_rows = self.fs.get_row(self.fs.income, ["Net Income"])
            ni = self.fs.latest(net_income_rows)

            total_assets_rows = self.fs.get_row(self.fs.balance, ["Total Assets"])
            curr_assets, prev_assets = self.fs.latest_and_prev(total_assets_rows)
            avg_assets = (curr_assets + prev_assets) / 2
            if avg_assets == 0:
                raise ValueError("Assets is 0") 
            return ni / avg_assets
        except Exception as e:
            raise RuntimeError(f"Failed to compute ROE: {e}") from e
        
    def roe(self) -> float:
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
                raise ValueError("Average equity is zero.")
            return ni / avg_eq
        except Exception as e:
            raise RuntimeError(f"Failed to compute ROE: {e}") from e