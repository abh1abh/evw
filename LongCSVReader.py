import polars as pl

class LongCSVReader:

    REQUIRED_COLS = ("Year", "Metric", "Value")

    def __init__(self, infer_schema_length: int = 2000) -> None:
        self.infer_schema_length = infer_schema_length

    def read_to_df(self, csv_path: str) -> pl.DataFrame:
        df_long = pl.read_csv(csv_path, infer_schema_length=self.infer_schema_length).drop_nulls()
        for col in self.REQUIRED_COLS:
            if col not in df_long.columns:
                raise ValueError(f"Missing required column: {col}")
        
        df_long = (
            df_long
            .with_columns([
                pl.col("Metric").cast(pl.Utf8),
                pl.col("Year").cast(pl.Int64, strict=False),
                pl.col("Value").cast(pl.Float64, strict=False)
            ])
            .filter(
                pl.col("Year").is_not_null()
                & pl.col("Metric").is_not_null()
                & (pl.col("Metric") != "")
                & pl.col("Value").is_not_null()
            )
            # If any duplicate (Year, Metric) slip in, keep the first
            .unique(subset=["Year", "Metric"], keep="first")
        )

        df_wide = df_long.pivot(values="Value", index="Year", columns="Metric", aggregate_function="first").sort("Year")
        return df_wide
    
    @staticmethod
    def write_csv(df: pl.DataFrame, out_path: str) -> None:
        df.write_csv(out_path)

