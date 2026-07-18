"""Build per-report market tables from a static source CSV.

All OHLCV data is bundled in a single long file (`data/source_data_long.csv`),
so no live downloads are required. This script maps the source symbols onto the
project's reference instruments, then slices a `--period` lookback window of
data ending on each market report date -- producing the `report_table_data/
<period>/` tables that `construct_dataset.py` consumes downstream.

Usage:
    python data/build_report_data.py --period "3 months"
    python data/build_report_data.py --period 1week --save-intermediate

`--period` accepts flexible forms: "1 day", "2 weeks", "1 month", "3 months",
"1 year", or the compact "1week" / "3months". Output goes to
`data/table_data/report_table_data/<period_label>/<split>/<market>-<source>/<report_date>.csv`.
"""

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Symbol mapping: source-CSV convention -> project reference convention.
#
# The source file uses barchart/stooq-style tickers, while the pipeline's
# reference files (financial_instrument_reference.json, futures_symbol.csv)
# use Yahoo/CME conventions. These tables bridge the two.
# ---------------------------------------------------------------------------

# Non-futures (equities, indices, FX, metals, energy, treasuries):
#   source symbol -> reference symbol (matches financial_instrument_reference.json).
SOURCE_TO_REF_SYMBOL: Dict[str, str] = {
    # --- equity indices ---
    "SPX": "^GSPC",            # S&P 500
    "IXIC": "^IXIC",           # NASDAQ Composite
    "DJI": "^DJI",             # Dow Jones Industrial Average
    "NDX": "^NDX",             # NASDAQ 100
    "RUT": "^RUT",             # Russell 2000
    "VIX": "^VIX",             # CBOE Volatility Index
    # --- S&P 500 GICS sectors (source SP500.<gics> -> Yahoo ^SP500-<gics>) ---
    "SP500.45": "^SP500-45",   # Information Technology
    "SP500.20": "^SP500-20",   # Industrials
    "SP500.40": "^SP500-40",   # Financials
    "SP500.35": "^SP500-35",   # Health Care
    "SP500.30": "^SP500-30",   # Consumer Staples
    "SP500.25": "^SP500-25",   # Consumer Discretionary
    "SP500.10": "^GSPE",       # Energy
    "SP500.60": "^SP500-60",   # Real Estate
    "SP500.55": "^SP500-55",   # Utilities
    "SP500.15": "^SP500-15",   # Materials
    "SP500.50": "^SP500-50",   # Communication Services
    # --- metals / dollar index / world index ---
    "XAUUSD": "^XAU",          # Gold
    "XAGUSD": "SI-F",          # Silver
    "DXY00": "DX-Y.NYB",       # US Dollar Index
    "XWD": "^990100-USD-STRD", # MSCI World index
    # --- energy ---
    "CL:NMX": "CL=F",          # WTI Crude Oil
    "BZ:NMX": "BZ=F",          # Brent Crude Oil
    "NG:NMX": "NG=F",          # Natural Gas
    # --- FX (quoted to match the Yahoo "=X" convention used in the reference) ---
    "EURUSD": "EUR=X",         # Euro
    "GBPUSD": "GBP=X",         # British Pound
    "AUDUSD": "AUD=X",         # Australian Dollar
    "USDJPY": "JPY=X",         # Japanese Yen
    #   (reference "Euro versus Pound" / EURGBP=X has no source counterpart.)
    # --- treasury yields ---
    "US12M": "TMUBMUSD01Y",    # 1-Year (12 months)
    "US2Y": "TMUBMUSD02Y",
    "US3Y": "TMUBMUSD03Y",
    "US5Y": "TMUBMUSD05Y",
    "US7Y": "TMUBMUSD07Y",
    "US10Y": "TMUBMUSD10Y",
    "US30Y": "TMUBMUSD30Y",
}

# Futures roots: source base -> reference base (matches futures_symbol.csv).
#   NOTE: the source provider uses DL for Class III Milk and DK for Class IV
#   Milk (barchart convention); the reference uses DC and GDK respectively.
SOURCE_TO_REF_FUTURES_BASE: Dict[str, str] = {
    "LE": "LE",    # Live Cattle
    "GF": "GF",    # Feeder Cattle
    "HE": "HE",    # Lean Hogs
    "KE": "KE",    # KC HRW Wheat
    "ZC": "ZC",    # Corn
    "ZW": "ZW",    # Chicago SRW Wheat
    "ZS": "ZS",    # Soybeans
    "ZL": "ZL",    # Soybean Oil
    "ZM": "ZM",    # Soybean Meal
    "DK": "GDK",   # Class IV Milk
    "DL": "DC",    # Class III Milk
}

# Source futures symbol pattern: <root><month-code><2-digit-year>, e.g. "LEG22".
# Continuous contracts ("LEY00", "GFY00", ...) use month code Y and are skipped.
_FUTURES_MONTH_CODES = "FGHJKMNQUVXZ"
_FUTURES_RE = re.compile(rf"^([A-Z]+?)([{_FUTURES_MONTH_CODES}])(\d{{2}})$")

# Decimal rounding by instrument type (FX -> 4, treasury -> 3, else 2).
_FX_SOURCE_SYMBOLS = {"EURUSD", "GBPUSD", "AUDUSD", "USDJPY"}
_TREASURY_SOURCE_SYMBOLS = {"US12M", "US2Y", "US3Y", "US5Y", "US7Y", "US10Y", "US30Y"}

PRICE_COLS = ["Open", "High", "Low", "Close"]
SELECTED_COLS = ["Date", "Product Name", "Symbol", "Open", "High", "Low", "Close", "Volume"]


# ---------------------------------------------------------------------------
# Period parsing
# ---------------------------------------------------------------------------

_UNIT_DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}


def parse_period(period: str) -> Tuple[int, str]:
    """Parse a period string into (lookback_days, label).

    Accepts "1 day", "2 weeks", "3 months", "1 year", or compact "1week".
    Months/years use the 30/365-day approximation already used by the
    downstream pipeline. The label is normalised to a singular, space-free
    form (e.g. "3 months" -> "3month") to match existing output directories.
    """
    match = re.fullmatch(r"\s*(\d+)\s*([a-zA-Z]+?)s?\s*", period)
    if not match:
        raise argparse.ArgumentTypeError(
            f"Invalid period {period!r}. Use forms like '1 day', '2 weeks', '3 months', '1 year'."
        )
    n = int(match.group(1))
    unit = match.group(2).lower()
    if unit not in _UNIT_DAYS:
        raise argparse.ArgumentTypeError(
            f"Unknown period unit {unit!r}. Supported units: day, week, month, year."
        )
    return n * _UNIT_DAYS[unit], f"{n}{unit}"


# ---------------------------------------------------------------------------
# Source -> processed_data conversion
# ---------------------------------------------------------------------------

def load_reference(reference_path: str) -> Tuple[List[Dict], Dict[str, str], Dict[str, str]]:
    """Return (reference items, ref-symbol -> name, futures-base -> product name)."""
    with open(reference_path, "r") as f:
        reference_data = json.load(f)

    symbol_to_name: Dict[str, str] = {}
    futures_base_to_name: Dict[str, str] = {}
    for item in reference_data:
        symbol = item.get("symbol") or ""
        if not symbol:
            continue
        if item["data_source"] == "cme":
            futures_base_to_name[symbol] = item["name"]
        else:
            symbol_to_name.setdefault(symbol, item["name"])
    return reference_data, symbol_to_name, futures_base_to_name


def _round_for(source_symbol: str) -> int:
    if source_symbol in _FX_SOURCE_SYMBOLS:
        return 4
    if source_symbol in _TREASURY_SOURCE_SYMBOLS:
        return 3
    return 2


def build_processed_data(
    raw: pd.DataFrame,
    symbol_to_name: Dict[str, str],
    futures_base_to_name: Dict[str, str],
) -> pd.DataFrame:
    """Map raw source rows to the processed_data schema used by the pipeline.

    Output columns: Date, Product Name, Symbol, Open, High, Low, Close, Volume
    where Symbol/Product Name follow the reference convention. Rows whose
    source symbol has no reference mapping are dropped.
    """
    records: List[pd.DataFrame] = []

    for source_symbol, group in raw.groupby("Symbol", sort=False):
        ref_symbol: Optional[str] = None
        product_name: Optional[str] = None

        if source_symbol in SOURCE_TO_REF_SYMBOL:
            ref_symbol = SOURCE_TO_REF_SYMBOL[source_symbol]
            product_name = symbol_to_name.get(ref_symbol)
        else:
            fmatch = _FUTURES_RE.match(str(source_symbol))
            if fmatch:
                base, month_code, yy = fmatch.groups()
                ref_base = SOURCE_TO_REF_FUTURES_BASE.get(base)
                if ref_base is not None:
                    ref_symbol = f"{ref_base}{month_code}{yy[-1]}"
                    product_name = futures_base_to_name.get(ref_base)

        if ref_symbol is None or product_name is None:
            continue

        block = group.copy()
        block["Symbol"] = ref_symbol
        block["Product Name"] = product_name
        block[PRICE_COLS] = block[PRICE_COLS].round(_round_for(source_symbol))
        records.append(block[SELECTED_COLS])

    if not records:
        return pd.DataFrame(columns=SELECTED_COLS)

    processed = pd.concat(records, ignore_index=True)
    processed = processed.drop_duplicates(["Date", "Product Name", "Symbol"])
    return processed.sort_values(["Product Name", "Symbol", "Date"]).reset_index(drop=True)


def load_source_data(source_path: str) -> pd.DataFrame:
    """Read and clean the long source CSV (mixed date formats, BOM, dup rows)."""
    df = pd.read_csv(source_path, encoding="utf-8-sig", low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    # Defensive: drop any concatenated header rows that leaked into the data.
    df = df[df["Symbol"] != "Symbol"]
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")
    df = df.dropna(subset=["Date"])
    # Numeric columns may carry comma thousands separators (e.g. "4,100.04").
    for col in PRICE_COLS + ["Volume"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce",
        )
    return df


# ---------------------------------------------------------------------------
# Per-report extraction (active-contract futures logic, source-agnostic)
# ---------------------------------------------------------------------------

class FuturesDataProcessor:
    def __init__(self, futures_data: pd.DataFrame):
        self.futures_data = futures_data

    def get_active_contracts(self, base_symbol: str, date: datetime, n: int = 3) -> pd.DataFrame:
        return self.futures_data[
            (self.futures_data["symbol"].str.startswith(base_symbol))
            & (self.futures_data["expiration_date"] > date)
        ].sort_values("expiration_date").head(n)

    @staticmethod
    def create_product_name(base_name: str, rank: int, expiration_date: datetime) -> str:
        rank_map = {1: "front month", 2: "second month", 3: "third month"}
        return f"{base_name} ({rank_map[rank]}) ({expiration_date.strftime('%B')})"


class MarketDataExtractor:
    def __init__(self, processed_data: pd.DataFrame, reference_data: List[Dict],
                 futures_processor: FuturesDataProcessor):
        self.processed_data = processed_data
        self.reference_data = reference_data
        self.futures_processor = futures_processor

    def _extract_futures_data(self, item: Dict, start_date: datetime,
                              end_date: datetime) -> pd.DataFrame:
        base_symbol = item["symbol"]
        active_futures = self.futures_processor.get_active_contracts(base_symbol, end_date)
        active_symbols = active_futures["symbol"].tolist()
        if not active_symbols:
            return pd.DataFrame(columns=self.processed_data.columns)

        market_data = self.processed_data[
            (self.processed_data["Symbol"].isin(active_symbols))
            & (self.processed_data["Date"] >= start_date)
            & (self.processed_data["Date"] <= end_date)
        ].copy()

        for rank, (_, future) in enumerate(active_futures.iterrows(), 1):
            mask = market_data["Symbol"] == future["symbol"]
            market_data.loc[mask, "Product Name"] = self.futures_processor.create_product_name(
                item["name"], rank, future["expiration_date"]
            )
        return market_data.sort_values(["Product Name", "Date"]).reset_index(drop=True)

    def _extract_symbol_data(self, item: Dict, start_date: datetime,
                             end_date: datetime) -> pd.DataFrame:
        return self.processed_data[
            (self.processed_data["Symbol"] == item["symbol"])
            & (self.processed_data["Date"] >= start_date)
            & (self.processed_data["Date"] <= end_date)
        ]

    def _extract_product_data(self, item: Dict, start_date: datetime,
                              end_date: datetime) -> pd.DataFrame:
        return self.processed_data[
            (self.processed_data["Product Name"] == item["name"])
            & (self.processed_data["Date"] >= start_date)
            & (self.processed_data["Date"] <= end_date)
        ]

    def extract_market_data(self, market: str, start_date: datetime,
                            end_date: datetime) -> pd.DataFrame:
        market_items = [item for item in self.reference_data if item["market"] == market]
        market_data = pd.DataFrame()
        for item in market_items:
            if item["data_source"] == "cme" and item["symbol"]:
                data = self._extract_futures_data(item, start_date, end_date)
            elif item["symbol"]:
                data = self._extract_symbol_data(item, start_date, end_date)
            else:
                data = self._extract_product_data(item, start_date, end_date)
            market_data = pd.concat([market_data, data])
        if market_data.empty:
            return market_data
        return market_data.drop_duplicates(["Date", "Product Name", "Symbol"])


class ReportTableBuilder:
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self._initialize_data()

    def _initialize_data(self):
        self.reference_data, symbol_to_name, futures_base_to_name = load_reference(
            self.config["reference_data_path"]
        )

        raw = load_source_data(self.config["source_data_path"])
        self.processed_data = build_processed_data(raw, symbol_to_name, futures_base_to_name)
        if self.config.get("intermediate_path"):
            out = Path(self.config["intermediate_path"])
            out.parent.mkdir(parents=True, exist_ok=True)
            self.processed_data.to_csv(out, index=False)
            print(f"Wrote {len(self.processed_data)} processed rows to {out}")

        report_data = pd.read_csv(
            self.config["report_data_path"], parse_dates=["date"], sep="\t", encoding="utf-16"
        )
        split_ref = pd.read_csv(self.config["split_ref_path"], parse_dates=["date"])
        self.report_data = pd.merge(report_data, split_ref, on=["source", "market", "date"])

        futures_data = pd.read_csv(
            self.config["futures_data_path"], parse_dates=["expiration_date"]
        )
        self.market_extractor = MarketDataExtractor(
            self.processed_data, self.reference_data, FuturesDataProcessor(futures_data)
        )

    def process_reports(self, lookback_days: int):
        written = 0
        for _, report in self.report_data.iterrows():
            start_date = report["date"] - timedelta(days=lookback_days)
            if self._process_single_report(
                report["market"], report["source"], report["date"], start_date, report["split"]
            ):
                written += 1
        print(f"Done. Wrote {written} report tables under {self.config['output_base_path']}")

    def _process_single_report(self, market: str, source: str, report_date: datetime,
                               start_date: datetime, split: str) -> bool:
        market_data = self.market_extractor.extract_market_data(market, start_date, report_date)
        if market_data.empty:
            print(f"No data found for {market} on {report_date.strftime('%Y-%m-%d')}")
            return False

        output_dir = Path(self.config["output_base_path"]) / split / f"{market.replace(' ', '_')}-{source}"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{report_date.strftime('%Y-%m-%d')}.csv"
        market_data.to_csv(output_path, index=False)
        return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--period", type=parse_period, default=parse_period("1week"),
        help="Lookback window per report, e.g. '1 day', '2 weeks', '3 months', '1 year'.",
    )
    parser.add_argument("--source-data", default="data/source_data_long.csv")
    parser.add_argument("--reports", default="data/reports/reports.tsv")
    parser.add_argument("--reference", default="data/references/financial_instrument_reference.json")
    parser.add_argument("--futures", default="data/references/futures_symbol.csv")
    parser.add_argument("--split-ref", default="data/references/split_ref.csv")
    parser.add_argument("--output-base", default="data/table_data/report_table_data")
    parser.add_argument(
        "--save-intermediate", action="store_true",
        help="Also write the combined processed_data CSV used internally.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    lookback_days, period_label = args.period

    config = {
        "reference_data_path": args.reference,
        "source_data_path": args.source_data,
        "report_data_path": args.reports,
        "split_ref_path": args.split_ref,
        "futures_data_path": args.futures,
        "output_base_path": f"{args.output_base}/{period_label}",
        "intermediate_path": (
            f"data/table_data/intermediate/processed_data_{period_label}.csv"
            if args.save_intermediate else None
        ),
    }

    print(f"Building report tables with a {period_label} ({lookback_days}-day) lookback window...")
    builder = ReportTableBuilder(config)
    builder.process_reports(lookback_days=lookback_days)


if __name__ == "__main__":
    main()
