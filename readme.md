# Market Report Generation Dataset

This repository contains code for constructing and evaluating a market report generation dataset. The pipeline processes financial market data from various sources and pairs it with market reports to create training datasets for language models.

## 1. Dataset Construction Pipeline

All OHLCV market data is bundled in `data/source_data_long.csv` (long format:
`Date, Symbol, Open, High, Low, Close, Volume`), so no live downloads or manual
collection are required. The pipeline consists of three scripts run sequentially.

#### Step 1: Build Report Tables (`build_report_data.py`)
```bash
python data/build_report_data.py --period "1 month"
```

**Objectives:**
- Read `source_data_long.csv` and map its symbols onto the project's reference
  instruments (`data/references/financial_instrument_reference.json`,
  `futures_symbol.csv`)
- For each market report, extract the OHLCV window covering the `--period`
  lookback ending on the report date (futures use the active front/second/third
  month contracts)
- Organize the output by historical time span, split, market, and data source

**Arguments:**
- `--period` — lookback window per report: `1 day`, `2 weeks`, `1 month`,
  `3 months`, `1 year`, or compact forms like `1week` / `3months` (default `1week`)
- `--save-intermediate` — also write the combined `processed_data` CSV used internally
- `--source-data`, `--reports`, `--reference`, `--futures`, `--split-ref`,
  `--output-base` — override default input/output paths

**Output Structure:**
```
data/
└── table_data/
    └── report_table_data/
        └── <historical_time_span>/
            └── <split>/
                └── <market-report_data_source>/
                    └── <report_date>.csv
```

#### Step 2: Construct Dataset (`construct_dataset.py`)
```bash
python construct_dataset.py
```

**Objectives:**
- Combine table data with corresponding market reports
- Format prompts for model training
- Include relevant metadata

**Output Structure:**
```
data/
└── processed_dataset/
    └── <historical_time_span>/
        └── <split>.json        # Contains tables, prompts, reports, and metadata
```

#### Step 3: Tokenize Dataset (`tokenize_dataset.py`)
```bash
python tokenize_dataset.py
```

**Objectives:**
- Convert processed dataset into tokenized format
- Prepare data for training open-source language models
- Support multiple tokenizer options

**Output Structure:**
```
data/
└── tokenized_dataset/
    └── <historical_time_span>/
        └── <tokenizer>/
            └── <split>/        # Tokenized data ready for training
```
