"""
data_store.py
--------------
Loads the two curated CSVs. Deliberately no live scraping in this
version — see README for why. Small, dated, sourced data beats a
large, unverifiable dataset for a decision this consequential.
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def load_scholarships() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "scholarships.csv")


def load_country_outcomes() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "country_fmge_outcomes.csv")
