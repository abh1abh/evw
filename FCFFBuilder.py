import numpy as np
import polars as pl

class FCFFBuilder:

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def compute_delta_nwc(df_wide: pl.DataFrame) -> pl.DataFrame:
        """
        ΔNWC = (AR + Inventory - AP)_t - (AR + Inventory - AP)_{t-1}
        Falls back to provided ChangeIn* columns if raw levels are missing.
        """
        has_raw = all(c in df_wide.columns for c in ("AccountsReceivable", "Inventory", "AccountsPayable"))
        if has_raw:
            df = df_wide.with_columns(
                (pl.col("AccountsReceivable").fill_null(0)
                 + pl.col("Inventory").fill_null(0)
                 - pl.col("AccountsPayable").fill_null(0)).alias("NWC_level")
            ).with_columns(
                (pl.col("NWC_level") - pl.col("NWC_level").shift(1)).alias("DeltaNWC")
            ).drop("NWC_level")
        else:
            for c in ("ChangeInAR", "ChangeInInventory", "ChangeInAP"):
                if c not in df_wide.columns:
                    raise ValueError("NWC inputs missing and no change-series found.")
            df = df_wide.with_columns(
                (pl.col("ChangeInAR").fill_null(0)
                 + pl.col("ChangeInInventory").fill_null(0)
                 - pl.col("ChangeInAP").fill_null(0)).alias("DeltaNWC")
            )
        return df

    @staticmethod
    def estimate_tax_rate(df: pl.DataFrame) -> pl.Series:
        """Effective tax rate per year ≈ TaxExpense / max(EBT, small_positive), clamped to [0, 0.5]."""
        if "EBT" not in df.columns or "TaxExpense" not in df.columns:
            return pl.Series([0.21] * df.height)  # fallback
        ebt_np = np.maximum(df.get_column("EBT").fill_null(0).to_numpy(), 1e-9)
        tax_np = np.maximum(df.get_column("TaxExpense").fill_null(0).to_numpy(), 0)
        rate = np.clip(tax_np / ebt_np, 0.0, 0.5)
        return pl.Series(rate)

    def compute_fcff(self, df_wide: pl.DataFrame) -> pl.DataFrame:
        required = ["OperatingIncome", "DepreciationAmortization", "Capex"]
        for c in required:
            if c not in df_wide.columns:
                raise ValueError(f"{c} is required to compute FCFF.")
        df = self.compute_delta_nwc(df_wide)
        tax_rate = self.estimate_tax_rate(df)

        df = df.with_columns(pl.Series("TaxRateEst", tax_rate))

        df = df.with_columns([
            (pl.col("OperatingIncome") * (1 - pl.col("TaxRateEst"))).alias("NOPAT"),
            pl.col("DepreciationAmortization").alias("DA"),
            pl.col("Capex").alias("CapexOut"),
        ])

        df = df.with_columns(
            (pl.col("NOPAT") + pl.col("DA") - pl.col("CapexOut") - pl.col("DeltaNWC")).alias("FCFF")
        )

        return df