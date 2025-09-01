import pandas as pd
import numpy as np
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
    
    def _get_tax_rate_series(self) -> pd.Series | None:
        # Prefer explicit tax rate if available (yfinance can surface it on balance in your map)
        tr = self.fs.get_metric("Tax Rate For Calcs")
        if tr is not None:
            return tr.astype(float)

        # Fallback: effective tax rate = Tax Provision / Pretax Income
        tax_prov = self.fs.get_metric("Tax Provision")
        pretax   = self.fs.get_metric("Pretax Income")
        if tax_prov is None or pretax is None:
            return None

        # Avoid division issues
        tr_fallback = (tax_prov.astype(float)) / (pretax.replace(0, np.nan).astype(float))
        # Optionally clip to a sane range [0, 0.5] to avoid data quirks
        tr_fallback = tr_fallback.clip(lower=0.0, upper=0.6)
        return tr_fallback

    def _get_ebit_series(self) -> pd.Series | None:
        # Prefer EBIT if present; else fall back to Operating Income
        ebit = self.fs.get_metric("EBIT")
        if ebit is not None:
            return ebit.astype(float)
        op_inc = self.fs.get_metric("Operating Income")
        if op_inc is not None:
            return op_inc.astype(float)
        return None

    def _get_da_series(self) -> pd.Series | None:
        da = self.fs.get_metric("Depreciation And Amortization")
        return da.astype(float) if da is not None else None

    def _capex_series(self) -> pd.Series | None:
        """
        Capex ≈ ΔNetPPE + D&A
        (When cash-flow 'Purchases of PPE' isn't available from yfinance.)
        """
        net_ppe = self.fs.get_metric("Net PPE")
        da      = self._get_da_series()
        if net_ppe is None or da is None:
            return None

        net_ppe = net_ppe.astype(float)
        da      = da.reindex_like(net_ppe).astype(float).fillna(0.0)

        # ΔNetPPE = current - previous (align by columns/index)
        delta_net_ppe = net_ppe - net_ppe.shift(-1)
        # Capex (cash outflow, positive) = ΔNetPPE + D&A
        capex = (delta_net_ppe + da).fillna(0.0)
        return capex

    def _operating_nwc_series(self) -> pd.Series | None:
        """
        Operating NWC = (Current Assets - Cash & Equivalents) - (Current Liabilities - Short Term Debt)
        (We exclude cash/equivalents and interest-bearing short-term debt.)
        """
        ca   = self.fs.get_metric("Current Assets")
        cl   = self.fs.get_metric("Current Liabilities")
        cash = self.fs.get_metric("Cash And Cash Equivalents")
        std  = self.fs.get_metric("Short Term Debt")

        if ca is None or cl is None:
            return None

        ca   = ca.astype(float)
        cl   = cl.astype(float)
        cash = cash.astype(float) if cash is not None else pd.Series(0.0, index=ca.index)
        std  = std.astype(float)  if std  is not None else pd.Series(0.0, index=cl.index)

        # Reindex to a common index (intersection) to avoid alignment issues
        common_idx = ca.index.intersection(cl.index).intersection(cash.index).intersection(std.index)
        ca   = ca.reindex(common_idx)
        cl   = cl.reindex(common_idx)
        cash = cash.reindex(common_idx).fillna(0.0)
        std  = std.reindex(common_idx).fillna(0.0)

        nwc_oper = (ca - cash) - (cl - std)
        return nwc_oper

    def fcff_series_from_statements(self) -> pd.Series | None:
        """
        FCFF_t = EBIT_t * (1 - TaxRate_t) + D&A_t - Capex_t - ΔNWC_t
        Returns a pd.Series indexed by period (yfinance columns).
        """
        ebit     = self._get_ebit_series()
        tax_rate = self._get_tax_rate_series()
        da       = self._get_da_series()
        capex    = self._capex_series()
        nwc_op   = self._operating_nwc_series()

        if any(x is None for x in (ebit, tax_rate, da, capex, nwc_op)):
            return None

        # Align everything to common index
        idx = ebit.index.intersection(tax_rate.index).intersection(da.index).intersection(capex.index).intersection(nwc_op.index)
        ebit     = ebit.reindex(idx).astype(float)
        tax_rate = tax_rate.reindex(idx).astype(float).ffill().bfill().clip(lower=0.0, upper=0.6)
        da       = da.reindex(idx).astype(float).fillna(0.0)
        capex    = capex.reindex(idx).astype(float).fillna(0.0)
        nwc_op   = nwc_op.reindex(idx).astype(float)

        # ΔNWC_t = NWC_t - NWC_{t-1}; with columns sorted desc by FSAccessor already.
        delta_nwc = nwc_op - nwc_op.shift(-1)
        delta_nwc = delta_nwc.fillna(0.0)

        # Compute FCFF with a while loop (your preference)
        fcff = pd.Series(index=idx, dtype="float64")
        cols = list(idx)  # periods in descending order per FSAccessor._sort_columns
        i = 0
        while i < len(cols):
            col = cols[i]
            nopat = ebit[col] * (1.0 - tax_rate[col])
            fcff[col] = nopat + da[col] - capex[col] - delta_nwc[col]
            i += 1

        return fcff

    def fcff_latest(self) -> float | None:
        """
        Convenience: returns the latest-period FCFF (requires at least 2 periods for Δ terms).
        """
        s = self.fcff_series_from_statements()
        if s is None or s.dropna().empty:
            return None
        # Latest column is first (sorted desc). If Δ values need prior period, fcff_series already handled shift.
        try:
            return float(s.dropna().iloc[0])
        except Exception:
            return None
    
    def dcf(self):
        fcff =self.fcff_series_from_statements()
        
        return fcff