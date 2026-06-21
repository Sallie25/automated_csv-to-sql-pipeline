# Automated CSV to SQL Pipeline

An automated ETL (Extract, Transform, Load) pipeline that ingests multiple CSV files, cleans and transforms the data, and loads it into a SQLite database — scheduled to run every Monday at 08:00 AM.

---

## Project Structure

```
Task1_csv_pipeline/
│
├── data/
│   └── raw/                    ← Drop your CSV files here
│       ├── customer_orders.csv
│       ├── employees.csv
│       ├── inventory.csv
│       ├── payroll.csv
│       ├── product_returns.csv
│       ├── project_tasks.csv
│       ├── sales_q1.csv
│       ├── store_branches.csv
│       ├── supplier_invoices.csv
│       ├── training_records.csv
│       └── website_traffic.csv
│
├── pipeline.py                 ← Ingestion & loading (Step 1)
├── transform.py                ← Data cleaning layer (Step 2)
├── scheduler.py                ← Weekly automation (Step 3)
│
├── pipeline.db                 ← SQLite database (auto-created)
├── pipeline.log                ← Activity log (auto-created)
├── pyproject.toml              ← uv project config & dependencies
├── uv.lock                     ← Locked dependency versions
└── README.md                   ← This file
```

---

## What the Pipeline Does

```
CSV files in data/raw/
        ↓
  pipeline.py          — finds all .csv files, reads each one
        ↓
  transform.py         — cleans and standardises the data
        ↓
  pipeline.db          — loads each file into its own SQL table
        ↓
  pipeline.log         — records every action and any errors
        ↓
  scheduler.py         — repeats automatically every Monday 08:00
```

---

## Data Cleaning Steps (transform.py)

Every CSV file is passed through five cleaning steps before loading:

| Step | What It Does | Example |
|---|---|---|
| 1. Clean column names | Lowercase + underscores | `"First Name"` → `first_name` |
| 2. Remove duplicates | Drops identical rows | 2 duplicate rows removed |
| 3. Handle missing values | Fills text with `"Unknown"`, numbers with `0` | Empty cells filled |
| 4. Fix data types | Converts date and numeric columns | `"$1,200"` → `1200.0` |
| 5. Add audit columns | Adds `loaded_at` and `source_file` | Traceability metadata |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Core language |
| uv | Project & dependency management |
| pandas | Reading CSVs and data manipulation |
| sqlalchemy | Database connection and loading |
| sqlite | File-based SQL database (no server needed) |
| schedule | Weekly automation |
| logging | Activity and error logging |
| pathlib | File system navigation |

---

## Setup & Installation

### Prerequisites
- Python 3.8 or newer
- [uv](https://docs.astral.sh/uv/) installed globally

### Install uv (if not already installed)
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone the repository
```bash
git clone https://github.com/Sallie25/automated_csv-to-sql-pipeline.git
cd automated_csv-to-sql-pipeline/Task1_csv_pipeline
```

### Install dependencies
```bash
uv sync
```

---

## Running the Pipeline

### Run once manually
```bash
uv run pipeline.py
```

### Run on a schedule (every Monday at 08:00)
```bash
uv run scheduler.py
```

> ⚠️ Keep the terminal open — closing it stops the scheduler.

### Test the scheduler immediately (fires after 1 minute)
In `scheduler.py`, uncomment this line:
```python
schedule.every(1).minutes.do(run)
```
Then run `uv run scheduler.py` and confirm it fires.

---

## Sample Output

```
2026-06-21 18:00:26  INFO  Scheduler started. Waiting for next Monday at 08:00...
2026-06-21 18:01:26  INFO  Scheduled run starting...
2026-06-21 18:01:26  INFO  Found 11 CSV file(s)
2026-06-21 18:01:26  INFO  Processing: employees.csv - table: 'employees'
2026-06-21 18:01:26  INFO    Shape of employees before transformation: 11 rows x 8 columns
2026-06-21 18:01:26  INFO    Starting transformation...
2026-06-21 18:01:26  INFO    Removed 1 duplicate(s)
2026-06-21 18:01:26  INFO    Done. 1 rows removed.
2026-06-21 18:01:26  INFO    Shape of employees after transformation: 10 rows x 10 columns
2026-06-21 18:01:27  INFO    [OK] Loaded into 'employees'
...
2026-06-21 18:01:33  INFO  Pipeline complete — 11 loaded, 0 failed
2026-06-21 18:01:33  INFO  Scheduled run complete.
```

---

## Error Handling

The pipeline is fault-tolerant — if one file fails, the rest continue processing. Errors are caught and logged without crashing the pipeline:

```
2026-06-21 18:01:47  ERROR  [FAILED] Failed to process website_traffic.csv:
                             Error tokenizing data. Expected 8 fields, saw 9
...
INFO  Pipeline complete — 10 loaded, 1 failed
```

---

## Database Tables Created

Each CSV file loads into its own dedicated SQL table:

| CSV File | SQL Table |
|---|---|
| customer_orders.csv | `customer_orders` |
| employees.csv | `employees` |
| inventory.csv | `inventory` |
| payroll.csv | `payroll` |
| product_returns.csv | `product_returns` |
| project_tasks.csv | `project_tasks` |
| sales_q1.csv | `sales_q1` |
| store_branches.csv | `store_branches` |
| supplier_invoices.csv | `supplier_invoices` |
| training_records.csv | `training_records` |
| website_traffic.csv | `website_traffic` |

Each table includes two extra audit columns added during transformation:
- `loaded_at` — timestamp of when the pipeline ran
- `source_file` — name of the original CSV file

---

## Querying the Database

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///pipeline.db")

# Query any table
df = pd.read_sql("SELECT * FROM employees", engine)
print(df)
```

---

## Adding New CSV Files

1. Drop any `.csv` file into `data/raw/`
2. Run `uv run pipeline.py`
3. A new SQL table is created automatically — no code changes needed

---

## Future Improvements

- Add support for cloud storage (AWS S3, Google Drive)
- Send email alerts on pipeline completion or failure
- Build a live dashboard with Streamlit
- Add a `processed_files.txt` tracker to prevent duplicate loads
- Support PostgreSQL for production deployments

---

## Author

**Salome Gabriel**  
GitHub: [@Sallie25](https://github.com/Sallie25)