# Bank Statement Analyzer

Simple Python script to analyze a bank statement CSV file and visualize spending trends.

## What It Does

- Opens a file picker to select a CSV file.
- Detects whether the CSV has headers (`date`, `description`, `withdrawal`, `deposit`, `balance`).
- Parses transaction amounts and dates.
- Calculates overall average total amounts for:
  - Per month
  - Per week
  - Per day
- Plots a combined chart:
  - Bars for daily total withdrawals and deposits
  - Line for daily net balance trend (`deposits - withdrawals`)

## Requirements

- Python 3.9+
- `matplotlib`

Install dependencies:

```bash
pip install matplotlib
```

## CSV Format

The script supports either:

1. Header-based CSV with these column names (case-insensitive):
   - `date`
   - `description`
   - `withdrawal`
   - `deposit`
   - `balance`
2. CSV without headers, assumed order:
   1. date
   2. description
   3. withdrawal
   4. deposit
   5. balance

Supported date formats:

- `MM/DD/YYYY`
- `MM/DD/YY`
- `YYYY-MM-DD`
- `DD/MM/YYYY`
- `DD-MM-YYYY`

Amount values may include `$` and commas (for example: `$1,234.56`).

## Run

From the project folder:

```bash
python main.py
```

Then select your statement CSV in the file picker window.

## Output

Console output includes:

- Detected column indexes
- Overall average total withdrawal and deposit amounts per month/week/day
- Number of rows skipped due to unrecognized date formats (if any)

A matplotlib window displays the combined trend chart.
