import yfinance as yf
from functools import reduce, cached_property
import pandas as pd
from typing import Iterable, Tuple
from dataclasses import dataclass
import logging
import operator

@dataclass
class FSAccessor:
    ticker: yf.Ticker

    METRIC_DEFINITIONS = {
        # Income Statement Metrics
        "Total Revenue": {
            "statement": "income",
            "primary_keys": ["Total Revenue", "Operating Revenue"],
            "derivation": None,
        },
        "Cost Of Revenue": {
            "statement": "income",
            "primary_keys": ["Cost Of Revenue", "Cost Of Goods Sold"],
            "derivation": None,
        },
        "Gross Profit": {
            "statement": "income",
            "primary_keys": ["Gross Profit"],
            "derivation": {
                "operator": "subtract",
                "operands": ["Total Revenue", "Cost Of Revenue"],
            },
        },
        "Operating Income": {
            "statement": "income",
            "primary_keys": ["Operating Income", "Total Operating Income As Reported"],
            "derivation": {
                "operator": "subtract",
                "operands": ["Gross Profit", "Operating Expense"],
            },
        },
        "Operating Expense": {
            "statement": "income",
            "primary_keys": ["Operating Expense"],
            "derivation": None,
        },
        "Net Income": {
            "statement": "income",
            "primary_keys": ["Net Income", "Net Income Common Stockholders"],
            "derivation": None,
        },
        "EBITDA": {
            "statement": "income",
            "primary_keys": ["EBITDA", "Normalized EBITDA"],
            "derivation": {
                "operator": "add",
                "operands": ["EBIT", "Depreciation And Amortization"],
            },
        },
        "EBIT": {
            "statement": "income",
            "primary_keys": ["EBIT"],
            "derivation": {
                "operator": "add",
                "operands": ["Net Income", "Interest Expense", "Tax Provision"],
            },
        },
        "Interest Expense": {
            "statement": "income",
            "primary_keys": ["Interest Expense"],
            "derivation": None,
        },
        "Tax Provision": {
            "statement": "income",
            "primary_keys": ["Tax Provision", "Income Tax Expense"],
            "derivation": {
                "operator": "subtract",
                "operands": ["Pretax Income", "Net Income"],
            },
        },
        "Pretax Income": {
            "statement": "income",
            "primary_keys": ["Pretax Income", "Income Before Tax"],
            "derivation": {
                "operator": "subtract",
                "operands": ["EBIT", "Interest Expense"],
            },
        },
        "Depreciation And Amortization": {
            "statement": "income",
            "primary_keys": ["Depreciation And Amortization", "Reconciled Depreciation"],
            "derivation": None,
        },
        "Diluted EPS": {
            "statement": "income",
            "primary_keys": ["Diluted EPS", "Basic EPS"],
            "derivation": None,
        },
        "Tax Rate For Calcs": {
            "statement": "income",
            "primary_keys": ["Tax Rate For Calcs"],
            "derivation": None,
        },
        # Balance Sheet Metrics
        "Total Assets": {
            "statement": "balance",
            "primary_keys": ["Total Assets"],
            "derivation": {
                "operator": "add",
                "operands": ["Total Liabilities", "Stockholders Equity"],
            },
        },
        "Current Assets": {
            "statement": "balance",
            "primary_keys": ["Current Assets"],
            "derivation": None,
        },
        "Current Liabilities": {
            "statement": "balance",
            "primary_keys": ["Current Liabilities"],
            "derivation": None,
        },
        "Inventory": {
            "statement": "balance",
            "primary_keys": ["Inventory"],
            "derivation": None,
        },
        "Accounts Receivable": {
            "statement": "balance",
            "primary_keys": ["Accounts Receivable", "Receivables"],
            "derivation": None,
        },
        "Stockholders Equity": {
            "statement": "balance",
            "primary_keys": [
                "Stockholders Equity",
                "Common Stock Equity",
                "Total Stockholder Equity",
            ],
            "derivation": {
                "operator": "subtract",
                "operands": ["Total Assets", "Total Liabilities"],
            },
        },
        "Total Liabilities": {
            "statement": "balance",
            "primary_keys": ["Total Liabilities"],
            "derivation": None,
        },
        "Total Debt": {
            "statement": "balance",
            "primary_keys": ["Total Debt"],
            "derivation": {
                "operator": "add",
                "operands": ["Short Term Debt", "Long Term Debt"],
            },
        },
        "Short Term Debt": {
            "statement": "balance",
            "primary_keys": [
                "Short Term Debt",
                "Current Debt",
                "Current Debt And Capital Lease Obligation",
                "Other Current Borrowings",
                "Commercial Paper",
            ],
            "derivation": None,
        },

        "Long Term Debt": {
            "statement": "balance",
            "primary_keys": ["Long Term Debt"],
            "derivation": None,
        },
        "Cash And Cash Equivalents": {
            "statement": "balance",
            "primary_keys": ["Cash And Cash Equivalents", "Cash"],
            "derivation": None,
        },
        "Net PPE": {
            "statement": "balance",
            "primary_keys": ["Net PPE"],
            # Optional: derive if Net PPE missing
            # Net PPE = Gross PPE - Accumulated Depreciation
            "derivation": {
                "operator": "subtract",
                "operands": ["Gross PPE", "Accumulated Depreciation"],
            },
        },
    }

    @cached_property
    def income(self) -> pd.DataFrame:
        df = self.ticker.financials.copy()
        return self._sort_columns(df)

    @cached_property
    def balance(self) -> pd.DataFrame:
        df = self.ticker.balance_sheet.copy()
        return self._sort_columns(df)
    
    @staticmethod
    def _sort_columns(df: pd.DataFrame) -> pd.DataFrame:
        # yfinance columns are datelike strings; coerce to datetime and sort desc
        cols = pd.to_datetime(df.columns, errors="coerce")
        order = pd.Series(range(len(cols)), index=df.columns)
        if cols.notna().all():
            order = pd.Series(cols, index=df.columns).sort_values(ascending=False)
            return df.loc[:, order.index]
        return df  # fallback: leave as-is

    def get_row(self, df: pd.DataFrame, keys: Iterable[str]) -> pd.Series | None:
        for k in keys:
            if k in df.index:
                return df.loc[k]
        return None


    def latest_and_prev(self, row: pd.Series) -> Tuple[float, float]:
        # Ensure we have at least 2 columns
        vals = row.dropna().astype(float)
        if len(vals) < 2:
            raise ValueError(f"Need at least two periods for average. Got: {vals.to_dict()}")
        return float(vals.iloc[0]), float(vals.iloc[1])
    
    def latest(self, row: pd.Series) -> float:
        # Ensure we have at least 1 column
        vals = row.dropna().astype(float)
        if len(vals) < 1:
            raise ValueError(f"Need at least one period. Got: {vals.to_dict()}")
        return float(vals.iloc[0])
    
    def get_metric(self, metric_name: str) -> pd.Series | None:
        """
        Retrieves a financial metric series from the income statement or balance sheet.

        This function follows a tiered fallback system:
        1. Direct Lookup: Tries to find the metric by its primary names.
        2. Derivation: If not found, it tries to calculate it based on rules
           defined in METRIC_DEFINITIONS.
        3. Graceful Failure: If both fail, it returns None.

        Args:
            metric_name: The standardized name of the metric to retrieve.

        Returns:
            A pandas Series for the metric if found or derived, otherwise None.
        """
        # 1. Look up the metric definition
        metric_def = self.METRIC_DEFINITIONS.get(metric_name)
        if not metric_def:
            logging.warning(f"For ticker {self.ticker.ticker}, metric '{metric_name}' is not defined in METRIC_DEFINITIONS.")
            return None

        # 2. Determine which financial statement to use
        statement_df = self.income if metric_def["statement"] == "income" else self.balance

        # 3. Direct Lookup
        row = self.get_row(statement_df, metric_def["primary_keys"])
        if row is not None:
            return row

        logging.debug(f"For ticker {self.ticker.ticker}, '{metric_name}' not found directly. Attempting derivation.")

        # 4. Derivation Fallback
        derivation_rule = metric_def.get("derivation")
        if derivation_rule:
            op_str = derivation_rule["operator"]
            operands = derivation_rule["operands"]
            
            operand_series = []
            for op_name in operands:
                op_series = self.get_metric(op_name)
                if op_series is None:
                    logging.warning(f"For ticker {self.ticker.ticker}, failed to derive '{metric_name}' because operand '{op_name}' could not be found or derived.")
                    operand_series = [] # Mark as failed
                    break
                operand_series.append(op_series)

            if operand_series:
                try:
                    # Make a list of series, filling NaNs with 0 for calculations
                    filled_operands = [s.fillna(0) for s in operand_series]
                    
                    result = None
                    if op_str == "add":
                        result = reduce(operator.add, filled_operands)
                    elif op_str == "subtract":
                        result = reduce(operator.sub, filled_operands)
                    
                    if result is not None:
                        logging.debug(f"For ticker {self.ticker.ticker}, '{metric_name}' was successfully derived from {operands}.")
                        return result

                except (TypeError, ValueError):
                    logging.error(f"For ticker {self.ticker.ticker}, a calculation error occurred while deriving '{metric_name}'.")
                    return None

        # 5. Graceful Failure
        logging.warning(f"For ticker {self.ticker.ticker}, the metric '{metric_name}' could not be found or derived.")
        return None