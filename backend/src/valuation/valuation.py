from core import yf, FSAccessor
import logging

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

    def price_per_share(self) -> float | None:
        try:
            return self.ticker.history(period="1d")["Close"].iloc[-1]
        except Exception:
            logging.exception("Error fetching Price per Share")
            return None

    def book_value_per_share(self) -> float | None:
        try:
            equity = self.fs.latest(self.fs.get_row(self.fs.balance, ["Common Stock Equity"]))
            shares = self.ticker.info.get("sharesOutstanding")
            if not shares or shares == 0:
                return None
            return equity / shares
        except Exception:
            logging.exception("Error Calculating Book Value per Share")
            return None

    def enterprise_value(self) -> float | None:
        try:
            market_cap = self.ticker.info.get("marketCap")
            debt = self.fs.latest(self.fs.get_row(self.fs.balance, ["Total Debt"]))
            cash = self.fs.latest(self.fs.get_row(self.fs.balance, ["Cash And Cash Equivalents"]))
            return market_cap + debt - cash
        except Exception:
            logging.exception("Error calculating Enterprise value")
            return None

    def pe_ratio(self) -> float | None:
        try:
            price = self.price_per_share()
            eps = self.fs.latest(self.fs.get_row(self.fs.income, ["Diluted EPS"]))
            if price is None or eps is None or eps <= 0:
                return None
            return price / eps
        except Exception:
            logging.exception("Error Calculating P/E ratio")
            return None
    
    def pb_ratio(self) -> float | None:
        try:
            price = self.price_per_share()
            bvps = self.book_value_per_share()
            if price is None or bvps is None or bvps <= 0:
                return None
            return price / bvps
        except Exception:
            logging.exception("Error Calculating P/B ratio")
            return None

    def ev_ebitda(self) -> float | None:
        try:
            enterprise_value = self.enterprise_value()
            ebitda = self.fs.latest(self.fs.get_row(self.fs.income, ["EBITDA"]))
            if enterprise_value is None or ebitda is None or ebitda <= 0:
                return None
            return enterprise_value / ebitda
        except Exception:
            logging.exception("Error Calculating EV/EBITDA ratio")
            return None
        
