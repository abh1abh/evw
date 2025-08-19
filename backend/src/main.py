from __future__ import annotations
import argparse
import json
from pathlib import Path
from LongCSVReader import LongCSVReader
from FCFFBuilder import FCFFBuilder
import yfinance as yf
from roe import Roe
from roa import Roa
from margins import Margin

def main():
    parser = argparse.ArgumentParser(
        description=( "EVW MVP: read long-format CSV, compute FCFF, run DCF, write outputs."
    ))
    parser.add_argument("-t", "--ticker", required=True, help="Path to CSV: Year,Metric,Value")
    # parser.add_argument("-o", "--output_path", required=True, help="Output path")
    parser.add_argument("--wacc", type=float, default=0.08)
    parser.add_argument("--ltg", type=float, default=0.025)
    parser.add_argument("--midyear", action="store_true", default=True)
    parser.add_argument("--no-midyear", dest="midyear", action="store_false")
    parser.add_argument("--horizon", type=int, default=5)
    parser.add_argument("--net-debt", type=float, default=None)
    args = parser.parse_args()
    
    ticker = yf.Ticker(args.ticker)

    # print(ticker.financials)
    
    roe = Roe(ticker=ticker).calc_roe()   

    print("ROE: ", roe)

    roa = Roa(ticker=ticker).calc_roa()

    print("ROA: ", roa)


    margin = Margin(ticker=ticker)
    print("Margins: ")
    print("Gross ", margin.calc_gross_profit_margin())
    print("Operating ", margin.calc_operating_margin())
    print("Net ", margin.calc_net_margin())
    print("EBITDA ", margin.calc_ebitda_margin())

    
    # out = Path(args.output_path)
    # out.mkdir(parents=True, exist_ok=True)

    # reader = LongCSVReader()
    # df = reader.read_to_df(args.input)
    # print(df)
    # reader.write_csv(df, str(out / "wide_financials.csv"))


    # fcff_builder = FCFFBuilder()
    # fcff_df = fcff_builder.compute_fcff(df)
    # fcff_df.select(["Year","NOPAT","DA","CapexOut","DeltaNWC","FCFF"]).write_csv(out / "fcff_components.csv")


if __name__ == "__main__":
    main()
    print("Done")
