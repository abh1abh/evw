from core import yf, FSAccessor
import logging

class WACCCalculator:
    def __init__(self, ticker: yf.Ticker):
        self.ticker = ticker
        self.fs = FSAccessor(ticker)

    def cost_of_equity(self, risk_free_rate: float, equity_risk_premium: float) -> float | None:
        """Calculates the cost of equity using the Capital Asset Pricing Model (CAPM)."""
        beta = self.ticker.info.get("beta")
        if beta is None:
            logging.warning(f"For ticker {self.ticker.ticker}, Beta not available. Cannot calculate Cost of Equity.")
            return None
        return risk_free_rate + beta * equity_risk_premium

    def cost_of_debt(self) -> float | None:
        """Estimates the cost of debt as Interest Expense / Total Debt."""
        interest_series = self.fs.get_metric("Interest Expense")
        debt_series = self.fs.get_metric("Total Debt")

        if interest_series is None or debt_series is None:
            return None # FSAccessor has already logged the reason.

        try:
            interest_expense = self.fs.latest(interest_series)
            total_debt = self.fs.latest(debt_series)

            if total_debt == 0:
                return 0.0
            
            return abs(interest_expense / total_debt)
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Cost of Debt due to insufficient data: {e}")
            return None

    def effective_tax_rate(self) -> float | None:
        """Calculates the effective tax rate from the income statement."""
        tax_series = self.fs.get_metric("Tax Provision")
        ebt_series = self.fs.get_metric("Pretax Income")

        if tax_series is None or ebt_series is None:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, Tax or Pretax income not found. Falling back to default rate.")
            return 0.21 # Fallback to a default rate

        try:
            tax_expense = self.fs.latest(tax_series)
            ebt = self.fs.latest(ebt_series)

            if ebt <= 0:
                return 0.0
            
            return tax_expense / ebt
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not calculate Effective Tax Rate due to insufficient data: {e}")
            return None

    def market_values(self) -> dict | None:
        """Gets the market value of equity and debt."""
        market_cap = self.ticker.info.get("marketCap")
        debt_series = self.fs.get_metric("Total Debt")

        if market_cap is None or debt_series is None:
            logging.warning(f"For ticker {self.ticker.ticker}, Market Cap or Total Debt not available.")
            return None

        try:
            total_debt = self.fs.latest(debt_series)
            return {"equity": market_cap, "debt": total_debt}
        except ValueError as e:
            logging.warning(f"For ticker {self.fs.ticker.ticker}, could not get market values due to insufficient data: {e}")
            return None

    def calculate(self, risk_free_rate: float, equity_risk_premium: float) -> float | None:
        """Calculates the Weighted Average Cost of Capital (WACC)."""
        market_vals = self.market_values()
        if market_vals is None: 
            return None
            
        mv_equity = market_vals["equity"]
        mv_debt = market_vals["debt"]
        
        total_value = mv_equity + mv_debt
        if total_value == 0:
            return 0.0

        weight_equity = mv_equity / total_value
        weight_debt = mv_debt / total_value

        re = self.cost_of_equity(risk_free_rate, equity_risk_premium)
        rd = self.cost_of_debt()
        tc = self.effective_tax_rate()

        if any(v is None for v in [re, rd, tc]):
            logging.warning(f"For ticker {self.ticker.ticker}, could not calculate WACC due to missing components (Cost of Equity, Debt, or Tax Rate).")
            return None

        wacc = (weight_equity * re) + (weight_debt * rd * (1 - tc))
        return wacc
