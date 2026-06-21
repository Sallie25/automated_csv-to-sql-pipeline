import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

def transform_dataframe(df, source_filename="unknown"):
    """
    Clean and standardise a raw DataFrame.
    Steps: clean column names, remove duplicates,
    handle missing values, fix data types, add audit columns.
    """
    logger.info("  Starting transformation...")
    df = df.copy()
    initial_rows = len(df)

    df = clean_column_names(df)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = fix_data_types(df)
    df = add_audit_columns(df, source_filename)

    logger.info(f"  Done. {initial_rows - len(df)} rows removed.")
    return df


def clean_column_names(df):
    """Standardise all column names to lowercase with underscores."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace(r"[^\w]", "_", regex=True)
    )
    return df


def remove_duplicates(df):
    """Drop completely identical rows."""
    before = len(df)
    df = df.drop_duplicates(keep="first")
    logger.info(f"  Removed {before - len(df)} duplicate(s)")
    return df


def handle_missing_values(df):
    """Drop fully empty rows; fill remaining nulls by type."""
    df = df.dropna(how="all")
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("Unknown")
        elif pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
    return df


def fix_data_types(df):
    """Auto-convert date and numeric columns."""
    for col in df.columns:
        if any(k in col for k in ["date", "time"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif any(k in col for k in ["amount", "price", "salary", "revenue", "cost", "qty", "quantity", "total"]):
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.replace(r"[$,]", "", regex=True).str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def add_audit_columns(df, source_filename):
    """Add metadata columns for traceability."""
    df["loaded_at"] = datetime.utcnow()
    df["source_file"] = source_filename
    return df