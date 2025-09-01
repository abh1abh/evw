from core import yf, FSAccessor
import logging

class WACCCalculator:
    def __init__(self, ticker: yf.Ticker):
        self.ticker = ticker
        self.fs = FSAccessor(ticker)

    def cost_of_equity(self, risk_free_rate: float, equity_risk_premium: float) -> float | None:
        """Calculates the cost of equity using the Capital Asset Pricing Model (CAPM)."""
        try:
            beta = self.ticker.info.get("beta")
            if beta is None:
                logging.warning("Beta not available for this ticker, cannot calculate Cost of Equity.")
                return None
            return risk_free_rate + beta * equity_risk_premium
        except Exception:
            logging.exception("Failed to calculate Cost of Equity")
            return None

    def cost_of_debt(self) -> float | None:
        """Estimates the cost of debt as Interest Expense / Total Debt."""
        try:
            interest_expense_row = self.fs.get_row(self.fs.income, ["Interest Expense"])
            interest_expense = self.fs.latest(interest_expense_row)
            
            total_debt_row = self.fs.get_row(self.fs.balance, ["Total Debt"])
            total_debt = self.fs.latest(total_debt_row)

            if total_debt == 0:
                return 0.0
            
            return abs(interest_expense / total_debt)
        except KeyError:
            logging.warning("Interest Expense or Total Debt not found. Cannot calculate Cost of Debt.")
            return 0.0
        except Exception:
            logging.exception("Failed to calculate Cost of Debt")
            return None

    def effective_tax_rate(self) -> float | None:
        """Calculates the effective tax rate from the income statement."""
        try:
            tax_expense_row = self.fs.get_row(self.fs.income, ["Tax Provision", "Income Tax Expense"])
            tax_expense = self.fs.latest(tax_expense_row)

            ebt_row = self.fs.get_row(self.fs.income, ["Pretax Income", "Income Before Tax"])
            ebt = self.fs.latest(ebt_row)

            if ebt <= 0:
                return 0.0
            
            return tax_expense / ebt
        except KeyError:
            logging.warning("Tax or Pretax income not found. Falling back to default rate.")
            return 0.21
        except Exception:
            logging.exception("Failed to calculate Effective Tax Rate")
            return None

    def market_values(self) -> dict | None:
        """Gets the market value of equity and debt."""
        try:
            market_cap = self.ticker.info.get("marketCap")
            if market_cap is None:
                raise ValueError("Market Cap not available.")

            total_debt = self.fs.latest(self.fs.get_row(self.fs.balance, ["Total Debt"]))
            
            return {"equity": market_cap, "debt": total_debt}
        except Exception:
            logging.exception("Failed to get market values")
            return None

    def calculate(self, risk_free_rate: float, equity_risk_premium: float) -> float | None:
        """Calculates the Weighted Average Cost of Capital (WACC)."""
        try:
            market_vals = self.market_values()
            if market_vals is None: return None
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
                logging.warning("Could not calculate WACC due to missing components (Cost of Equity, Debt, or Tax Rate).")
                return None

            wacc = (weight_equity * re) + (weight_debt * rd * (1 - tc))
            return wacc
        except Exception:
            logging.exception("Failed to calculate WACC")
            return None