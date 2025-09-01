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
        except IndexError:
            logging.warning(f"For ticker {self.ticker.ticker}, could not fetch price per share. No history returned.")
            return None

    def book_value_per_share(self) -> float | None:
        equity_series = self.fs.get_metric("Stockholders Equity")
        if equity_series is None:
            return None

        shares = self.ticker.info.get("sharesOutstanding")
        if not shares or shares == 0:
            logging.warning(f"For ticker {self.ticker.ticker}, shares outstanding are zero or unavailable.")
            return None

        try:
            equity = self.fs.latest(equity_series)
            return equity / shares
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Book Value per Share due to insufficient data: {e}")
            return None

    def enterprise_value(self) -> float | None:
        market_cap = self.ticker.info.get("marketCap")
        debt_series = self.fs.get_metric("Total Debt")
        cash_series = self.fs.get_metric("Cash And Cash Equivalents")

        if market_cap is None or debt_series is None or cash_series is None:
            return None

        try:
            debt = self.fs.latest(debt_series)
            cash = self.fs.latest(cash_series)
            return market_cap + debt - cash
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Enterprise Value due to insufficient data: {e}")
            return None

    def pe_ratio(self) -> float | None:
        price = self.price_per_share()
        eps_series = self.fs.get_metric("Diluted EPS")

        if price is None or eps_series is None:
            return None

        try:
            eps = self.fs.latest(eps_series)
            if eps <= 0:
                return None
            return price / eps
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate P/E Ratio due to insufficient data: {e}")
            return None
    
    def pb_ratio(self) -> float | None:
        price = self.price_per_share()
        bvps = self.book_value_per_share()

        if price is None or bvps is None or bvps <= 0:
            return None
        
        return price / bvps

    def ev_ebitda(self) -> float | None:
        ev = self.enterprise_value()
        ebitda_series = self.fs.get_metric("EBITDA")

        if ev is None or ebitda_series is None:
            return None

        try:
            ebitda = self.fs.latest(ebitda_series)
            if ebitda <= 0:
                return None
            return ev / ebitda
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate EV/EBITDA Ratio due to insufficient data: {e}")
            return None
        
