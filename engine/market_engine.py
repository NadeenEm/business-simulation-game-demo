import pandas as pd
import numpy as np

def run_market_simulation(week: int, companies_df: pd.DataFrame, decisions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple shared-market engine:
    - Uses BA decisions (role == 'BA') for price, quantity, marketing
    - All companies compete for the same market
    """

    week_dec = decisions_df[(decisions_df["week"] == week) & (decisions_df["role"] == "BA")]
    if week_dec.empty:
        return pd.DataFrame()

    df = week_dec.merge(companies_df, on="company_id", how="left")

    # Total market demand (you can customize per week or scenario)
    total_market_demand = df["base_demand"].mean() * len(df)

    # Sensitivities – tweak for your course
    beta_p = 0.05   # price sensitivity
    beta_m = 0.02   # marketing sensitivity

    # Attractiveness from price + marketing
    df["attr"] = np.exp(-beta_p * df["price"]) * (1 + beta_m * df["marketing"])
    df["market_share"] = df["attr"] / df["attr"].sum()

    # Demand allocation
    df["demand"] = df["market_share"] * total_market_demand

    # Respect quantity + capacity
    df["sold_qty"] = df[["demand", "quantity", "capacity"]].min(axis=1)

    # Economics
    df["revenue"] = df["sold_qty"] * df["price"]
    df["variable_cost"] = df["sold_qty"] * df["unit_cost"]
    df["total_cost"] = df["variable_cost"] + df["fixed_cost"]
    df["profit"] = df["revenue"] - df["total_cost"]

    # For now, score = profit (you can add penalties/bonuses later)
    df["score"] = df["profit"]

    results_cols = [
        "week","company_id","company_name","price","quantity","marketing",
        "market_share","demand","sold_qty","revenue","total_cost","profit","score"
    ]
    # rename company_name from companies.csv
    if "name" in df.columns and "company_name" not in df.columns:
        df = df.rename(columns={"name": "company_name"})
    return df[results_cols]
