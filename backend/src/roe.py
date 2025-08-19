from fs_accessor import yf, FSAccessor
class Roe:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)
    
    def calc_roe(self) -> float:
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
                raise ZeroDivisionError("Average equity is zero.")
            return ni / avg_eq
        except Exception as e:
            raise RuntimeError("Failed to compute ROE") from e