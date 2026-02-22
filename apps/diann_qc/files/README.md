# DIA-NN QC Dashboard

A Streamlit app for quality control of DIA-NN proteomics search engine output.
Supports both standard DIA (Orbitrap/QTOF) and diaPASEF (timsTOF) data.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
diann_qc_app/
├── app.py                  # Entry point, layout, sidebar
├── requirements.txt
├── utils/
│   ├── loader.py           # Parquet + metadata loading, regex extraction
│   ├── plots.py            # Shared Plotly theme + helpers
│   └── session.py          # Session state defaults
└── tabs/
    ├── tab_upload.py       # Tab 0 — Upload & Configure
    ├── tab_raw_qc.py       # Tab 1 — Raw Data QC
    ├── tab_summary.py      # Tab 2 — Summary Statistics
    ├── tab_analysis.py     # Tab 3 — Data Analysis
    └── tab_normalization.py # Tab 4 — Normalization
```

## Metadata file format

The metadata file should be a CSV or TSV with at minimum:

| sample_id   | group     | run_order | ... |
|-------------|-----------|-----------|-----|
| sample_001  | treatment | 1         |     |
| sample_002  | control   | 2         |     |

- `sample_id`: must match the IDs extracted from the `Run` column via the regex
- `group`: used for group-aware colouring throughout all tabs
- `run_order`: optional, used for run-order drift plots

## Regex examples

| Pattern | Extracts |
|---|---|
| `.*[\\/](.+?)(?:\.\w+)?$` | Filename stem (default) |
| `.*_(S\d+)_.*` | Sample number like `S042` |
| `(\w+)_DIA_.*` | Leading identifier |
