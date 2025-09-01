import argparse
import yfinance as yf
import logging

from ratios import Efficiency, Growth, Leverage, Liquidity, Profitability
from valuation import Valuation, WACCCalculator


def main():
    # --- Setup Logging ---
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--ticker", required=True, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--wacc", type=float, help="Directly input WACC, overriding calculation.")
    parser.add_argument("--risk-free-rate", default=0.04, type=float, help="Risk-free rate for CAPM.")
    parser.add_argument("--equity-risk-premium", default=0.05, type=float, help="Equity risk premium for CAPM.")
    parser.add_argument("--dcf", action="store_true")
 
    args = parser.parse_args()
    print("DCF: ",args.dcf)
    
    risk_free_rate = args.risk_free_rate
    equity_risk_premium = args.equity_risk_premium 

    ticker = yf.Ticker(args.ticker)
    # print(ticker.financials.index)
    # print(ticker.balance_sheet.index)


    def print_metric(name, value):
        print(f"{name:<25} {f'{value:.4f}' if value is not None else 'Not Available'}")

    profitability = Profitability(ticker)
    print("\nProfitability: ")
    print_metric("Return on Equity", profitability.roe())
    print_metric("Return on Assets", profitability.roa())
    print_metric("Gross Margin", profitability.gross_profit_margin())
    print_metric("Operating Margin", profitability.operating_margin())
    print_metric("Net Income Margin", profitability.net_margin())
    print_metric("EBITDA Margin", profitability.ebitda_margin())
    
    leverage = Leverage(ticker=ticker)
    print("\nLeverage: ")
    print_metric("Debt to Equity", leverage.debt_to_equity())
    print_metric("Debt ratio", leverage.debt_ratio())
    print_metric("Equity ratio", leverage.equity_ratio())
    print_metric("Interest Coverage", leverage.interest_coverage())

    efficiency = Efficiency(ticker=ticker)
    print("\nEfficiency: ")
    print_metric("Asset Turnover", efficiency.asset_turnover())
    print_metric("Inventory Turnover", efficiency.inventory_turnover())
    print_metric("Receivables Turnover", efficiency.receivables_turnover())

    growth = Growth(ticker=ticker)
    print("\nGrowth: ")
    print_metric("Revenue Growth", growth.revenue_growth())
    print_metric("Net Income Growth", growth.net_income_growth())
    print_metric("EPS Growth", growth.eps_growth())

    liquidity = Liquidity(ticker)
    print("\nLiquidity:")
    print_metric("Current Ratio", liquidity.current_ratio())
    print_metric("Quick Ratio", liquidity.quick_ratio())

    valuation = Valuation(ticker)
    print("\nValuation: ")
    print_metric("P/E Ratio", valuation.pe_ratio())
    print_metric("P/B Ratio", valuation.pb_ratio())
    print_metric("EV/EBITDA Ratio", valuation.ev_ebitda())

    # --- New WACC Calculation Section ---
    print("\nDiscount Rate (WACC):")
    if args.wacc:
        print_metric("WACC (provided)", args.wacc)
    else:
        wacc_calculator = WACCCalculator(ticker)
        wacc = wacc_calculator.calculate(risk_free_rate, equity_risk_premium)
        
        print_metric("Risk-Free Rate", risk_free_rate)
        print_metric("Equity Risk Premium", equity_risk_premium)
        print_metric("Cost of Equity (CAPM)", wacc_calculator.cost_of_equity(risk_free_rate, equity_risk_premium))
        print_metric("Cost of Debt", wacc_calculator.cost_of_debt())
        print_metric("Effective Tax Rate", wacc_calculator.effective_tax_rate())
        print_metric("WACC (calculated)", wacc)

        if(args.dcf):
            print("FCFF:\n", valuation.dcf())    

if __name__ == "__main__":
    main()
    print("Done")
