from __future__ import annotations
import argparse
from pathlib import Path
import yfinance as yf
from ratios import Efficiency, Growth, Leverage, Liquidity, Profitability
from valuation import Valuation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--ticker", required=True, help="Path to CSV: Year,Metric,Value")
 
    args = parser.parse_args()
    
    ticker = yf.Ticker(args.ticker)

    # print("Income:\n",ticker.financials.index)
    # print("Balance:\n",ticker.balance_sheet.index)

    profitability = Profitability(ticker)
    print("\nProfitability: ")
    print(f"Return on Equity:       {profitability.roe()}")
    print(f"Return on Assets:       {profitability.roa()}")
    print(f"Gross Margin:           {profitability.gross_profit_margin()}")
    print(f"Operating Margin:       {profitability.operating_margin()}")
    print(f"Net Income Margin:      {profitability.net_margin()}")
    print(f"EBITDA Margin:          {profitability.ebitda_margin()}")
    
    leverage = Leverage(ticker=ticker)
    print("\nLeverage: ")
    print(f"Debt to Equity:         {leverage.debt_to_equity()}")
    print(f"Debt ratio:             {leverage.debt_ratio()}")
    print(f"Equity ratio:           {leverage.equity_ratio()}")
    print(f"Interest Coverage:      {leverage.interest_coverage()}")

    efficiency = Efficiency(ticker=ticker)
    print("\nEfficiency: ")
    print(f"Asset Turnover:         {efficiency.asset_turnover()}")
    print(f"Inventory Turnover:     {efficiency.inventory_turnover()}")
    print(f"Receivables Turnover:   {efficiency.receivables_turnover()}")

    growth = Growth(ticker=ticker)
    print("\nGrowth: ")
    print(f"Revenue Growth:         {growth.revenue_growth()}")
    print(f"Net Income Growth:      {growth.net_income_growth()}")
    print(f"EPS Growth:             {growth.eps_growth()}")

    liquidity = Liquidity(ticker)
    print("\nLiquidity:")
    print(f"Current Ratio:          {liquidity.current_ratio()}")
    print(f"Quick Ratio:            {liquidity.quick_ratio()}")

    valuation = Valuation(ticker)
    print("\Valuation: ")
    print(f"P/E Ratio:              {valuation.pe_ratio()}")
    print(f"P/B Ratio:              {valuation.pb_ratio()}")
    print(f"EV/EBITDA Ratio:        {valuation.ev_ebitda()}")

if __name__ == "__main__":
    main()
    print("Done")
