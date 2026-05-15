import numpy as np
import pandas as pd
import pytest

from validate_data import check_duplicates, check_missing, check_outliers


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def clean_df():
    return pd.DataFrame({
        "age":    [25, 30, 35, 40, 45],
        "salary": [40000.0, 50000.0, 60000.0, 70000.0, 80000.0],
        "dept":   ["HR", "Sales", "Eng", "HR", "Sales"],
    })


@pytest.fixture
def df_with_missing():
    return pd.DataFrame({
        "age":    [25, np.nan, 35, np.nan, 45],
        "salary": [40000.0, 50000.0, np.nan, 70000.0, 80000.0],
        "dept":   ["HR", "Sales", "Eng", "HR", "Sales"],
    })


@pytest.fixture
def df_with_duplicates():
    return pd.DataFrame({
        "age":    [25, 30, 25, 40, 30],
        "salary": [40000.0, 50000.0, 40000.0, 70000.0, 50000.0],
        "dept":   ["HR", "Sales", "HR", "HR", "Sales"],
    })


@pytest.fixture
def df_with_outliers():
    # salary has two extreme outliers; age is clean
    return pd.DataFrame({
        "age":    list(range(20, 50)),
        "salary": [50000.0] * 28 + [1.0, 999999.0],
    })


# ── check_missing ─────────────────────────────────────────────────────────────

class TestCheckMissing:
    def test_no_missing_returns_empty(self, clean_df):
        result = check_missing(clean_df)
        assert result.empty

    def test_detects_missing_columns(self, df_with_missing):
        result = check_missing(df_with_missing)
        assert "age" in result.index
        assert "salary" in result.index

    def test_clean_column_not_in_result(self, df_with_missing):
        result = check_missing(df_with_missing)
        assert "dept" not in result.index

    def test_missing_count_is_correct(self, df_with_missing):
        result = check_missing(df_with_missing)
        assert result.loc["age", "missing_count"] == 2
        assert result.loc["salary", "missing_count"] == 1

    def test_missing_pct_is_correct(self, df_with_missing):
        result = check_missing(df_with_missing)
        assert result.loc["age", "missing_pct"] == pytest.approx(40.0)
        assert result.loc["salary", "missing_pct"] == pytest.approx(20.0)

    def test_all_missing_column(self):
        df = pd.DataFrame({"a": [np.nan, np.nan, np.nan]})
        result = check_missing(df)
        assert result.loc["a", "missing_count"] == 3
        assert result.loc["a", "missing_pct"] == pytest.approx(100.0)

    def test_single_row_missing(self):
        df = pd.DataFrame({"a": [np.nan]})
        result = check_missing(df)
        assert result.loc["a", "missing_pct"] == pytest.approx(100.0)


# ── check_duplicates ──────────────────────────────────────────────────────────

class TestCheckDuplicates:
    def test_no_duplicates(self, clean_df):
        result = check_duplicates(clean_df)
        assert result["duplicate_rows"] == 0
        assert result["duplicate_pct"] == 0.0

    def test_detects_duplicates(self, df_with_duplicates):
        result = check_duplicates(df_with_duplicates)
        assert result["duplicate_rows"] == 2

    def test_duplicate_pct_is_correct(self, df_with_duplicates):
        result = check_duplicates(df_with_duplicates)
        assert result["duplicate_pct"] == pytest.approx(40.0)

    def test_all_duplicates(self):
        df = pd.DataFrame({"a": [1, 1, 1], "b": [2, 2, 2]})
        result = check_duplicates(df)
        # first occurrence is not a duplicate; 2 of 3 rows are
        assert result["duplicate_rows"] == 2
        assert result["duplicate_pct"] == pytest.approx(200 / 3, rel=1e-3)

    def test_single_row_no_duplicate(self):
        df = pd.DataFrame({"a": [1]})
        result = check_duplicates(df)
        assert result["duplicate_rows"] == 0

    def test_returns_int_count(self, df_with_duplicates):
        result = check_duplicates(df_with_duplicates)
        assert isinstance(result["duplicate_rows"], int)


# ── check_outliers ────────────────────────────────────────────────────────────

class TestCheckOutliers:
    def test_no_outliers_returns_empty(self, clean_df):
        result = check_outliers(clean_df)
        assert result.empty

    def test_detects_outlier_column(self, df_with_outliers):
        result = check_outliers(df_with_outliers)
        assert "salary" in result.index

    def test_clean_column_not_flagged(self, df_with_outliers):
        result = check_outliers(df_with_outliers)
        assert "age" not in result.index

    def test_outlier_count_is_correct(self, df_with_outliers):
        result = check_outliers(df_with_outliers)
        assert result.loc["salary", "outlier_count"] == 2

    def test_outlier_pct_is_correct(self, df_with_outliers):
        result = check_outliers(df_with_outliers)
        expected_pct = round(2 / 30 * 100, 2)
        assert result.loc["salary", "outlier_pct"] == pytest.approx(expected_pct)

    def test_bounds_are_present(self, df_with_outliers):
        result = check_outliers(df_with_outliers)
        assert "lower_bound" in result.columns
        assert "upper_bound" in result.columns

    def test_ignores_non_numeric_columns(self):
        df = pd.DataFrame({"name": ["a", "a", "a", "b", "b"]})
        result = check_outliers(df)
        assert result.empty

    def test_uniform_data_no_outliers(self):
        df = pd.DataFrame({"val": [5.0] * 20})
        result = check_outliers(df)
        assert result.empty

    def test_single_extreme_value(self):
        values = [10.0] * 19 + [10000.0]
        df = pd.DataFrame({"val": values})
        result = check_outliers(df)
        assert "val" in result.index
        assert result.loc["val", "outlier_count"] == 1
