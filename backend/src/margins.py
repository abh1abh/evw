from fs_accessor import yf, FSAccessor

class Margin:
    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)

    def _revenue(self):
        rev_row = self.fs.get_row(self.fs.income, ["Total Revenue", "Operating Revenue"])
        rev, _ = self.fs.latest_and_prev(rev_row)
        if rev == 0:
            raise ZeroDivisionError("Revenue is zero.")
        return rev
    
    def calc_net_margin(self):
        try:
            net_income_row = self.fs.get_row(self.fs.income, ["Net Income", "Net Income Common Stockholders"])
            ni, _ = self.fs.latest_and_prev(net_income_row)
            rev = self._revenue()
            return ni / rev
        except Exception as e:
            raise RuntimeError("Failed to compute Net Margin") from e
        
    def calc_gross_profit_margin(self):
        try:
            gp_row = self.fs.get_row(self.fs.income, ["Gross Profit"])
            gp, _ = self.fs.latest_and_prev(gp_row)
            rev = self._revenue()
            return gp / rev
        except Exception as e:
            raise RuntimeError("Failed to compute Gross Margin") from e
    
    def calc_operating_margin(self):
        try:
            op_row = self.fs.get_row(self.fs.income, ["Operating Income", "Total Operating Income As Reported"])
            op, _ = self.fs.latest_and_prev(op_row)
            rev = self._revenue()
            return op / rev
        except Exception as e:
            raise RuntimeError("Failed to compute Operating Margin") from e
        
    def calc_ebitda_margin(self):
        try:
            ebitda_row = self.fs.get_row(self.fs.income, ["EBITDA", "Normalized EBITDA"])
            e, _ = self.fs.latest_and_prev(ebitda_row)
            rev = self._revenue()
            return e / rev
        except Exception as e:
            raise RuntimeError("Failed to compute EBITDA Margin") from e