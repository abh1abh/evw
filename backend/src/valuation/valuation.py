from core import yf, FSAccessor
"""
Valuation Ratios (if you include stock price data)

P/E Ratio = Price per Share / EPS

P/B Ratio = Market Price / Book Value per Share

EV/EBITDA = Enterprise Value / EBITDA

These help compare valuation relative to earnings or book value.
"""

class Valuation: 
    
    def __init__(self, ticker: yf.Ticker):
        self.fs = FSAccessor(ticker)
        self.ticker = ticker

    def price_per_share(self) -> float:
        try:
            return self.ticker.history(period="1d")["Close"].iloc[-1]
        except Exception as e:
            raise RuntimeError("Error fetching Price per Share")

    def book_value_per_share(self) -> float:
        try:
            equity = self.fs.latest(self.fs.get_row(self.fs.balance, ["Common Stock Equity"]))
            shares = self.ticker.info.get("sharesOutstanding")
            if not shares:
                raise ValueError("No Outstanding Shares")
            return equity / shares
        except Exception as e:
            raise RuntimeError("Error Calculating Book Value per Share")

    def enterprise_value(self) -> float:
        try:
            market_cap = self.ticker.info.get("marketCap")
            debt = self.fs.latest(self.fs.get_row(self.fs.balance, ["Total Debt"]))
            cash = self.fs.latest(self.fs.get_row(self.fs.balance, ["Cash And Cash Equivalents"]))
            return market_cap + debt - cash

        except Exception as e:
            raise RuntimeError("Error Enterprise value")

    def pe_ratio(self) -> float:
        try:
            price = self.price_per_share()
            eps = self.fs.latest(self.fs.get_row(self.fs.income, ["Diluted EPS"]))
            if eps <= 0:
                raise ValueError("EPS is zero or negative; P/E ratio not meaningful.")
            return price / eps
        except Exception as e:
            raise RuntimeError(f"Error Calculating P/E ratio: {e}") from e
    
    def pb_ratio(self) -> float:
        try:
            price = self.price_per_share()
            bvps = self.book_value_per_share()
            if bvps <= 0:
                raise ValueError("Book Value per Share is zero or negative; P/B ratio not meaningful.")
            return price / bvps
        except Exception as e:
            raise RuntimeError(f"Error Calculating P/B ratio {e}") from e

    def ev_ebitda(self) -> float:
        try:
            enterprise_value = self.enterprise_value()
            ebitda = self.fs.latest(self.fs.get_row(self.fs.income, ["EBITDA"]))
            if ebitda < 0 and ebitda:
                raise ValueError("EBITDA is zero or negative; EV/EBITDA ratio not meaningful.")
            return enterprise_value / ebitda
        except Exception as e:
            raise RuntimeError(f"Error Calculating P/B ratio {e}") from e
        
