import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_file: str | None = None, verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=handlers)


logger = logging.getLogger(__name__)


def check_missing(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.isnull().sum()
    pct = (counts / len(df) * 100).round(2)
    result = pd.DataFrame({"missing_count": counts, "missing_pct": pct})
    return result[result["missing_count"] > 0]


def check_duplicates(df: pd.DataFrame) -> dict:
    n_dupes = df.duplicated().sum()
    return {"duplicate_rows": int(n_dupes), "duplicate_pct": round(n_dupes / len(df) * 100, 2)}


def check_outliers(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number])
    rows = []
    for col in numeric.columns:
        q1, q3 = numeric[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (numeric[col] < lower) | (numeric[col] > upper)
        n_out = int(mask.sum())
        logger.debug("Column '%s': IQR bounds [%.4f, %.4f], outliers=%d", col, lower, upper, n_out)
        if n_out > 0:
            rows.append({
                "column":        col,
                "outlier_count": n_out,
                "outlier_pct":   round(n_out / len(df) * 100, 2),
                "lower_bound":   round(lower, 4),
                "upper_bound":   round(upper, 4),
                "min_value":     round(numeric[col].min(), 4),
                "max_value":     round(numeric[col].max(), 4),
            })
    return pd.DataFrame(rows).set_index("column") if rows else pd.DataFrame()


def _section(title: str) -> None:
    logger.info("%s", "=" * 60)
    logger.info("  %s", title)
    logger.info("%s", "=" * 60)


def validate(path: str) -> bool:
    """Return True if the file passes all checks, False otherwise."""
    logger.info("Loading file: %s", path)
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        logger.error("File not found: %s", path)
        sys.exit(1)
    except Exception as exc:
        logger.error("Failed to read CSV: %s", exc)
        sys.exit(1)

    logger.info("Shape: %d rows × %d columns", df.shape[0], df.shape[1])
    logger.debug("Columns: %s", list(df.columns))

    passed = True

    # ── Missing values ────────────────────────────────────────────
    _section("Missing Values")
    missing = check_missing(df)
    if missing.empty:
        logger.info("No missing values found.")
    else:
        passed = False
        logger.warning("Missing values detected in %d column(s):", len(missing))
        for col, row in missing.iterrows():
            logger.warning("  %-20s %d missing (%.2f%%)", col, row["missing_count"], row["missing_pct"])

    # ── Duplicate rows ────────────────────────────────────────────
    _section("Duplicate Rows")
    dupes = check_duplicates(df)
    if dupes["duplicate_rows"] == 0:
        logger.info("No duplicate rows found.")
    else:
        passed = False
        logger.warning("%d duplicate rows found (%.2f%% of total)", dupes["duplicate_rows"], dupes["duplicate_pct"])

    # ── Outliers (IQR) ────────────────────────────────────────────
    _section("Outliers (IQR method, numeric columns only)")
    outliers = check_outliers(df)
    if outliers.empty:
        logger.info("No outliers detected.")
    else:
        passed = False
        logger.warning("Outliers detected in %d column(s):", len(outliers))
        for col, row in outliers.iterrows():
            logger.warning(
                "  %-20s %d outliers (%.2f%%) | bounds [%.4f, %.4f] | range [%.4f, %.4f]",
                col,
                row["outlier_count"],
                row["outlier_pct"],
                row["lower_bound"],
                row["upper_bound"],
                row["min_value"],
                row["max_value"],
            )

    # ── Summary ───────────────────────────────────────────────────
    _section("Summary")
    if passed:
        logger.info("PASSED — no issues found.")
    else:
        logger.warning("FAILED — issues detected (see above).")

    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a CSV file for data quality issues.")
    parser.add_argument("csv_file", help="Path to the CSV file to validate")
    parser.add_argument("--log-file", metavar="PATH", help="Also write logs to this file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG-level logging")
    args = parser.parse_args()

    setup_logging(log_file=args.log_file, verbose=args.verbose)

    logger.info("Starting validation — %s", datetime.now().strftime(DATE_FORMAT))
    passed = validate(args.csv_file)
    logger.info("Validation complete — %s", "PASSED" if passed else "FAILED")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
