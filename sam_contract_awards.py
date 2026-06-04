"""
SAM.gov Contract Awards API - DHS Data Downloader
==================================================
Downloads contract award CSV files from SAM.gov for the Department of Homeland Security (DHS)
across up to 10 years of data, handles schema drift across yearly files, and produces:
  - Downloaded CSV files per fiscal year
  - A unified merged CSV
  - A SQL Server CREATE TABLE script covering all discovered columns

Usage:
    pip install requests pandas pyodbc sqlalchemy tqdm

    python sam_contract_awards.py \
        --api-key YOUR_SAM_API_KEY \
        --start-year 2015 \
        --end-year 2024 \
        --output-dir ./sam_downloads

Environment variable alternative:
    SAM_API_KEY=YOUR_KEY python sam_contract_awards.py

Author: Generated for DHS contract award analysis
"""

import argparse
import logging
import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://api.sam.gov/contract-awards/v1/search"

# DHS department code used as a filter in SAM.gov
# departmentId for DHS = "7012"  (FPDS/SAM department code)
DHS_DEPARTMENT_ID = "7012"

# How long to wait (seconds) between polling for the async extract file
POLL_INTERVAL_SECONDS = 15
MAX_POLL_ATTEMPTS = 40          # ~10 minutes max wait per request

# ---------------------------------------------------------------------------
# SAM API helpers
# ---------------------------------------------------------------------------

def request_extract(api_key: str, start_date: str, end_date: str) -> str | None:
    """
    Kick off an asynchronous CSV extract request for DHS awards
    in [start_date, end_date] (MM/DD/YYYY format).

    Returns the file-download URL string, or None on failure.
    """
    params = {
        "api_key": api_key,
        "format": "csv",
        "departmentId": DHS_DEPARTMENT_ID,
        "approvedDate": f"[{start_date},{end_date}]",
        # Fetch both Award and IDV records
        "limit": 1,          # Only needed to trigger async extract; ignored for CSV
    }

    log.info("Requesting extract for %s → %s ...", start_date, end_date)
    try:
        resp = requests.get(BASE_URL, params=params, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.error("Extract request failed: %s", exc)
        return None

    body = resp.json()

    # The API returns a fileUrl when the extract is queued
    file_url: str = (
        body.get("fileUrl")
        or body.get("extractFileUrl")
        or body.get("downloadUrl")
        or ""
    )
    if not file_url:
        log.warning("No fileUrl returned. Full response: %s", body)
        return None

    # Replace placeholder token with real API key
    file_url = file_url.replace("REPLACE_WITH_API_KEY", api_key)
    log.info("Extract queued. Polling URL: %s", file_url[:80] + "...")
    return file_url


def poll_and_download(file_url: str, dest_path: Path) -> bool:
    """
    Poll the extract URL until the file is ready, then download it.
    Returns True on success.
    """
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        log.info("  Poll attempt %d/%d ...", attempt, MAX_POLL_ATTEMPTS)
        try:
            resp = requests.get(file_url, timeout=120, stream=True)
        except requests.RequestException as exc:
            log.warning("  Poll request error: %s", exc)
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        content_type = resp.headers.get("Content-Type", "")

        if resp.status_code == 200 and "text/csv" in content_type:
            # File is ready - stream to disk
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            total = int(resp.headers.get("Content-Length", 0))
            with open(dest_path, "wb") as fh, tqdm(
                desc=dest_path.name,
                total=total,
                unit="B",
                unit_scale=True,
                leave=False,
            ) as bar:
                for chunk in resp.iter_content(chunk_size=8192):
                    fh.write(chunk)
                    bar.update(len(chunk))
            log.info("  ✓ Downloaded → %s (%.1f KB)", dest_path, dest_path.stat().st_size / 1024)
            return True

        elif resp.status_code == 202 or "application/json" in content_type:
            # Not ready yet
            log.info("  File not ready yet, waiting %ds ...", POLL_INTERVAL_SECONDS)
            time.sleep(POLL_INTERVAL_SECONDS)

        else:
            log.warning("  Unexpected status %d / content-type '%s'", resp.status_code, content_type)
            time.sleep(POLL_INTERVAL_SECONDS)

    log.error("Max poll attempts reached. File never became available.")
    return False


# ---------------------------------------------------------------------------
# Multi-year download
# ---------------------------------------------------------------------------

def download_yearly_csvs(api_key: str, start_year: int, end_year: int, output_dir: Path) -> list[Path]:
    """
    Download one CSV per fiscal year (Oct 1 – Sep 30) for DHS contracts.
    Returns a list of successfully downloaded file paths.
    """
    downloaded: list[Path] = []

    for year in range(start_year, end_year + 1):
        # Fiscal year: Oct 1 (prev year) – Sep 30 (current year)
        fy_start = f"10/01/{year - 1}"
        fy_end   = f"09/30/{year}"
        dest = output_dir / f"dhs_contracts_fy{year}.csv"

        if dest.exists():
            log.info("FY%d file already exists, skipping download: %s", year, dest)
            downloaded.append(dest)
            continue

        file_url = request_extract(api_key, fy_start, fy_end)
        if not file_url:
            log.error("Could not get extract URL for FY%d. Skipping.", year)
            continue

        success = poll_and_download(file_url, dest)
        if success:
            downloaded.append(dest)
        else:
            log.error("Failed to download FY%d data.", year)

        # Be polite to the API
        time.sleep(3)

    return downloaded


# ---------------------------------------------------------------------------
# CSV merging with schema drift handling
# ---------------------------------------------------------------------------

def merge_csvs(csv_paths: list[Path], output_dir: Path) -> pd.DataFrame:
    """
    Load all yearly CSVs, unify their (potentially different) columns,
    add a source_fiscal_year column, and return a single DataFrame.

    Columns present in some years but not others are filled with NULL/NaN.
    """
    log.info("Merging %d CSV files ...", len(csv_paths))
    frames: list[pd.DataFrame] = []

    for path in csv_paths:
        log.info("  Loading %s ...", path.name)
        try:
            df = pd.read_csv(
                path,
                dtype=str,           # Keep everything as string to avoid type conflicts
                low_memory=False,
                encoding="utf-8-sig",
            )
        except Exception as exc:
            log.warning("  Could not read %s: %s", path.name, exc)
            continue

        # Normalize column names: lowercase, strip, replace spaces/slashes with underscores
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(r"[\s/\\]+", "_", regex=True)
            .str.replace(r"[^a-z0-9_]", "", regex=True)
        )

        # Tag with fiscal year derived from filename (e.g. dhs_contracts_fy2020.csv)
        fy_tag = path.stem.split("fy")[-1] if "fy" in path.stem else "unknown"
        df.insert(0, "source_fiscal_year", fy_tag)
        df.insert(1, "source_file", path.name)

        frames.append(df)
        log.info("    Rows: %d | Columns: %d", len(df), len(df.columns))

    if not frames:
        log.error("No data frames loaded. Aborting merge.")
        return pd.DataFrame()

    # Concatenate – pandas automatically aligns on column names and fills NaN for missing columns
    merged = pd.concat(frames, ignore_index=True, sort=False)
    log.info("Merged shape: %d rows × %d columns", *merged.shape)

    merged_path = output_dir / "dhs_contracts_all_years_merged.csv"
    merged.to_csv(merged_path, index=False)
    log.info("Merged CSV saved → %s", merged_path)

    return merged


# ---------------------------------------------------------------------------
# SQL Server DDL generation
# ---------------------------------------------------------------------------

# Known columns with their preferred SQL Server types.
# Anything not in this map defaults to NVARCHAR(512).
COLUMN_TYPE_MAP: dict[str, str] = {
    # Identifiers
    "piid":                             "NVARCHAR(50)",
    "referenced_idv_piid":              "NVARCHAR(50)",
    "agency_id":                        "NVARCHAR(20)",
    "referenced_idv_agency_id":         "NVARCHAR(20)",
    "transaction_number":               "INT",
    "modification_number":              "NVARCHAR(20)",

    # Dates
    "date_signed":                      "DATE",
    "effective_date":                   "DATE",
    "last_modified_date":               "DATE",
    "completion_date":                  "DATE",
    "period_of_performance_start_date": "DATE",
    "period_of_performance_current_end_date": "DATE",
    "period_of_performance_potential_end_date": "DATE",
    "approved_date":                    "DATE",
    "fiscal_year":                      "SMALLINT",

    # Dollars
    "dollars_obligated":                "DECIMAL(20,2)",
    "total_dollars_obligated":          "DECIMAL(20,2)",
    "base_and_all_options_value":       "DECIMAL(20,2)",
    "base_and_exercised_options_value": "DECIMAL(20,2)",
    "action_obligation":                "DECIMAL(20,2)",

    # Awardee
    "awardee_uei":                      "NVARCHAR(20)",
    "awardee_duns":                     "NVARCHAR(20)",
    "awardee_name":                     "NVARCHAR(255)",
    "awardee_cage_code":                "NVARCHAR(10)",
    "awardee_address_line_1":           "NVARCHAR(255)",
    "awardee_city":                     "NVARCHAR(100)",
    "awardee_state":                    "NVARCHAR(50)",
    "awardee_zip":                      "NVARCHAR(20)",
    "awardee_country":                  "NVARCHAR(50)",

    # Agency / office info
    "department_id":                    "NVARCHAR(10)",
    "department_name":                  "NVARCHAR(255)",
    "sub_tier_id":                      "NVARCHAR(10)",
    "sub_tier_name":                    "NVARCHAR(255)",
    "contracting_office_id":            "NVARCHAR(10)",
    "contracting_office_name":          "NVARCHAR(255)",
    "funding_agency_id":                "NVARCHAR(10)",
    "funding_agency_name":              "NVARCHAR(255)",
    "funding_sub_tier_id":              "NVARCHAR(10)",
    "funding_sub_tier_name":            "NVARCHAR(255)",
    "funding_office_id":                "NVARCHAR(10)",
    "funding_office_name":              "NVARCHAR(255)",

    # Classification
    "psc_code":                         "NVARCHAR(10)",
    "psc_description":                  "NVARCHAR(255)",
    "naics_code":                       "NVARCHAR(10)",
    "naics_description":                "NVARCHAR(255)",
    "type_of_contract_pricing":         "NVARCHAR(100)",
    "contract_type":                    "NVARCHAR(50)",
    "solicitation_id":                  "NVARCHAR(50)",
    "award_type":                       "NVARCHAR(50)",
    "multi_year_contract":              "CHAR(1)",
    "number_of_actions":                "INT",
    "record_type":                      "NVARCHAR(20)",
    "set_aside_type":                   "NVARCHAR(100)",
    "set_aside_description":            "NVARCHAR(255)",
    "place_of_performance_city":        "NVARCHAR(100)",
    "place_of_performance_state":       "NVARCHAR(50)",
    "place_of_performance_zip":         "NVARCHAR(20)",
    "place_of_performance_country":     "NVARCHAR(50)",
    "place_of_performance_congressional_district": "NVARCHAR(10)",

    # Metadata added by this pipeline
    "source_fiscal_year":               "SMALLINT",
    "source_file":                      "NVARCHAR(100)",
}

# Columns that hint at date/dollar/int even if not in the explicit map
DATE_HINTS   = ("_date", "date_", "fiscal_year", "signed")
DOLLAR_HINTS = ("dollars", "obligated", "value", "amount", "cost")
INT_HINTS    = ("number_of", "_count", "_qty")


def infer_sql_type(col: str) -> str:
    """Return the best SQL Server type for a normalized column name."""
    if col in COLUMN_TYPE_MAP:
        return COLUMN_TYPE_MAP[col]
    for hint in DATE_HINTS:
        if hint in col:
            return "DATE"
    for hint in DOLLAR_HINTS:
        if hint in col:
            return "DECIMAL(20,2)"
    for hint in INT_HINTS:
        if hint in col:
            return "INT"
    return "NVARCHAR(512)"


def generate_sql_ddl(df: pd.DataFrame, table_name: str = "dbo.dhs_contract_awards") -> str:
    """
    Generate a SQL Server CREATE TABLE statement from the merged DataFrame's columns.
    Includes a surrogate PK, all discovered columns, and common index hints.
    """
    lines: list[str] = []
    lines.append(f"-- =============================================================")
    lines.append(f"-- SQL Server DDL for DHS Contract Awards (SAM.gov)")
    lines.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"-- Covers all columns discovered across downloaded fiscal-year CSVs")
    lines.append(f"-- =============================================================")
    lines.append("")
    lines.append(f"IF OBJECT_ID(N'{table_name}', N'U') IS NOT NULL")
    lines.append(f"    DROP TABLE {table_name};")
    lines.append("GO")
    lines.append("")
    lines.append(f"CREATE TABLE {table_name} (")
    lines.append("")
    lines.append("    -- Surrogate primary key")
    lines.append("    contract_award_sk   BIGINT          IDENTITY(1,1)  NOT NULL,")
    lines.append("")
    lines.append("    -- Pipeline metadata")
    lines.append("    source_fiscal_year  SMALLINT        NULL,   -- FY of the source CSV")
    lines.append("    source_file         NVARCHAR(100)   NULL,   -- filename the row came from")
    lines.append("    load_timestamp      DATETIME2       NOT NULL  DEFAULT SYSUTCDATETIME(),")
    lines.append("")
    lines.append("    -- Contract Award columns (union of all fiscal years)")

    # Skip metadata columns already written above
    skip_cols = {"source_fiscal_year", "source_file"}
    col_defs: list[str] = []

    for col in df.columns:
        if col in skip_cols:
            continue
        sql_type = infer_sql_type(col)
        col_defs.append(f"    {col:<55} {sql_type:<22} NULL")

    lines.append(",\n".join(col_defs))
    lines.append("")
    lines.append(f"    CONSTRAINT PK_{table_name.replace('dbo.', '')} PRIMARY KEY CLUSTERED (contract_award_sk)")
    lines.append(");")
    lines.append("GO")
    lines.append("")
    lines.append("-- =============================================================")
    lines.append("-- Recommended indexes")
    lines.append("-- =============================================================")
    lines.append("")

    index_cols = [
        ("piid",               "Contract PIID lookup"),
        ("date_signed",        "Date-range queries"),
        ("approved_date",      "Approval date queries"),
        ("source_fiscal_year", "Per-FY filtering"),
        ("awardee_uei",        "Vendor lookups"),
        ("naics_code",         "Industry analysis"),
        ("psc_code",           "Product/service analysis"),
        ("department_id",      "Department (DHS subtier) filtering"),
    ]

    existing_cols = set(df.columns)
    for i, (col, comment) in enumerate(index_cols, start=1):
        if col in existing_cols:
            lines.append(f"-- {comment}")
            lines.append(f"CREATE NONCLUSTERED INDEX IX_{table_name.replace('dbo.', '')}_{col}")
            lines.append(f"    ON {table_name} ({col});")
            lines.append("GO")
            lines.append("")

    lines.append("-- =============================================================")
    lines.append("-- Optional: full-text index for description columns")
    lines.append("-- (Requires full-text search feature enabled in SQL Server)")
    lines.append("-- =============================================================")
    lines.append("")
    lines.append(f"-- CREATE FULLTEXT CATALOG dhs_contracts_catalog AS DEFAULT;")
    lines.append(f"-- CREATE FULLTEXT INDEX ON {table_name}(psc_description, naics_description, awardee_name)")
    lines.append(f"--     KEY INDEX PK_{table_name.replace('dbo.', '')};")
    lines.append("-- GO")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Optional: bulk-load helper (pyodbc)
# ---------------------------------------------------------------------------

def build_bulk_insert_sql(csv_path: Path, table_name: str = "dbo.dhs_contract_awards") -> str:
    """
    Returns a BULK INSERT T-SQL statement to load the merged CSV into SQL Server.
    Edit the DATA_SOURCE or file path as appropriate for your environment.
    """
    return f"""
-- =============================================================
-- Bulk load merged CSV into SQL Server
-- Adjust the file path and format file as needed
-- =============================================================
BULK INSERT {table_name}
FROM '{csv_path.resolve()}'
WITH (
    FORMAT          = 'CSV',
    FIRSTROW        = 2,           -- skip header row
    FIELDTERMINATOR = ',',
    ROWTERMINATOR   = '\\n',
    CODEPAGE        = '65001',     -- UTF-8
    TABLOCK
);
GO
"""


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download DHS contract award CSVs from SAM.gov and generate SQL Server DDL"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("SAM_API_KEY", ""),
        help="SAM.gov Public API Key (or set SAM_API_KEY env var)",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2015,
        help="First fiscal year to download (e.g. 2015 = FY2015, Oct 2014 – Sep 2015)",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=datetime.now().year,
        help="Last fiscal year to download (default: current year)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./sam_downloads"),
        help="Directory to write CSV files and SQL script",
    )
    parser.add_argument(
        "--table-name",
        default="dbo.dhs_contract_awards",
        help="SQL Server table name for the DDL script",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip API download; re-merge and regenerate DDL from existing CSVs in --output-dir",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.api_key and not args.skip_download:
        log.error(
            "No API key provided. Pass --api-key or set the SAM_API_KEY environment variable.\n"
            "  Get your key at: https://sam.gov/workspace/profile/account-details"
        )
        raise SystemExit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    log.info("Output directory: %s", args.output_dir.resolve())

    # ---- Step 1: Download ------------------------------------------------
    if args.skip_download:
        log.info("--skip-download set. Looking for existing CSVs in %s ...", args.output_dir)
        csv_files = sorted(args.output_dir.glob("dhs_contracts_fy*.csv"))
        if not csv_files:
            log.error("No dhs_contracts_fy*.csv files found in %s", args.output_dir)
            raise SystemExit(1)
        log.info("Found %d existing CSV files.", len(csv_files))
    else:
        csv_files = download_yearly_csvs(
            api_key=args.api_key,
            start_year=args.start_year,
            end_year=min(args.end_year, args.start_year + 9),  # cap at 10 years
            output_dir=args.output_dir,
        )
        if not csv_files:
            log.error("No files downloaded. Check your API key and network connectivity.")
            raise SystemExit(1)

    # ---- Step 2: Merge ---------------------------------------------------
    merged_df = merge_csvs(csv_files, args.output_dir)
    if merged_df.empty:
        log.error("Merged DataFrame is empty. Aborting.")
        raise SystemExit(1)

    # ---- Step 3: Column report -------------------------------------------
    col_report_path = args.output_dir / "column_report.txt"
    with open(col_report_path, "w") as fh:
        fh.write(f"Column Availability Report\n")
        fh.write(f"Generated: {datetime.now().isoformat()}\n")
        fh.write(f"{'='*60}\n\n")
        fh.write(f"Total unique columns across all files: {len(merged_df.columns)}\n\n")
        fh.write(f"{'Column Name':<55} {'SQL Type':<22} {'Non-Null %':>10}\n")
        fh.write("-" * 90 + "\n")
        total = len(merged_df)
        for col in sorted(merged_df.columns):
            non_null_pct = 100.0 * merged_df[col].notna().sum() / total if total else 0
            fh.write(f"{col:<55} {infer_sql_type(col):<22} {non_null_pct:>9.1f}%\n")
    log.info("Column report saved → %s", col_report_path)

    # ---- Step 4: Generate SQL DDL ----------------------------------------
    ddl = generate_sql_ddl(merged_df, table_name=args.table_name)
    ddl_path = args.output_dir / "create_table_dhs_contract_awards.sql"
    ddl_path.write_text(ddl, encoding="utf-8")
    log.info("SQL DDL saved → %s", ddl_path)

    # ---- Step 5: Bulk Insert helper SQL ----------------------------------
    merged_csv_path = args.output_dir / "dhs_contracts_all_years_merged.csv"
    bulk_sql = build_bulk_insert_sql(merged_csv_path, args.table_name)
    bulk_sql_path = args.output_dir / "bulk_insert_dhs_contracts.sql"
    bulk_sql_path.write_text(bulk_sql, encoding="utf-8")
    log.info("Bulk insert SQL saved → %s", bulk_sql_path)

    # ---- Summary ---------------------------------------------------------
    log.info("")
    log.info("=" * 60)
    log.info("DONE. Output files:")
    for path in sorted(args.output_dir.iterdir()):
        size_kb = path.stat().st_size / 1024
        log.info("  %-50s %8.1f KB", path.name, size_kb)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
