from fs_accessor import yf, FSAccessor


class Roa:

    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)      
        
    
    def calc_roa(self):
        try:
            net_income_rows = self.fs.get_row(self.fs.income, ["Net Income"])
            ni, _ = self.fs.latest_and_prev(net_income_rows)

            total_assets_rows = self.fs.get_row(self.fs.balance, ["Total Assets"])
            curr_assets, prev_assets = self.fs.latest_and_prev(total_assets_rows)
            avg_assets = (curr_assets + prev_assets) / 2
            if avg_assets == 0:
                raise ZeroDivisionError("Assets is 0") 
            return ni / avg_assets
        except Exception as e:
            raise RuntimeError("Failed to compute ROE") from e
 