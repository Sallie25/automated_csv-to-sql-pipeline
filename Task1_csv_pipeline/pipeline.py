import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# Folder containing raw CSV files
raw_data_path = Path("data/raw")

# Find all CSV files
csv_files = list(raw_data_path.glob("*.csv"))

if not csv_files:
    print("No CSV files found in data/raw/")
    exit()

print(f"Found {len(csv_files)} CSV file(s)\n")

# Create SQLite database connection
engine = create_engine("sqlite:///pipeline.db")


def clean_table_name(file_path: Path) -> str:
    """
    Convert filename into a safe SQL table name.
    Example: sales-data_2024.csv → sales_data_2024
    """
    return file_path.stem.replace("-", "_").replace(" ", "_").lower()


for file in csv_files:
    table_name = clean_table_name(file)

    print(f"\nProcessing file: {file.name}")
    print(f"Target table: {table_name}")

    # Read CSV into DataFrame
    df = pd.read_csv(file)

    # Print shape
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # Load into its OWN table
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",  # overwrite per file
        index=False
    )

    print(f"Loaded into table: {table_name}")

print("\nPipeline completed successfully.")
