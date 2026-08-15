
import csv
from collections import defaultdict
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt


def parse_amount(value):
    cleaned = value.strip().strip('"').replace('$', '').replace(',', '')
    return float(cleaned) if cleaned else 0.0


def parse_date(date_text):
    cleaned = date_text.strip().strip('"')
    formats = [
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def average(total, count):
    return total / count if count else 0.0


def select_csv_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])


def get_column_indexes(file_path):
    with open(file_path, 'r', newline='') as file_obj:
        reader = csv.reader(file_obj)
        first_row = next(reader, [])

    columns = [col.strip().strip('"').lower() for col in first_row]
    required = ['date', 'description', 'withdrawal', 'deposit', 'balance']
    has_headers = all(column in columns for column in required)

    if has_headers:
        indexes = {
            'date': columns.index('date'),
            'description': columns.index('description'),
            'withdrawal': columns.index('withdrawal'),
            'deposit': columns.index('deposit'),
            'balance': columns.index('balance'),
        }
    else:
        indexes = {
            'date': 0,
            'description': 1,
            'withdrawal': 2,
            'deposit': 3,
            'balance': 4,
        }

    return indexes, has_headers


def load_data(file_path, indexes, has_headers):
    data = []
    with open(file_path, 'r', newline='') as file_obj:
        reader = csv.reader(file_obj)

        if has_headers:
            next(reader, None)

        for row in reader:
            if not row:
                continue

            date = row[indexes['date']] if indexes['date'] < len(row) else ''
            description = row[indexes['description']] if indexes['description'] < len(row) else ''
            withdrawal = parse_amount(row[indexes['withdrawal']]) if indexes['withdrawal'] < len(row) else 0.0
            deposit = parse_amount(row[indexes['deposit']]) if indexes['deposit'] < len(row) else 0.0
            balance = parse_amount(row[indexes['balance']]) if indexes['balance'] < len(row) else 0.0

            data.append({
                'date': date,
                'description': description,
                'withdrawal': withdrawal,
                'deposit': deposit,
                'balance': balance,
            })

    return data


def update_group_totals(group_totals, key, withdrawal, deposit):
    group_totals[key]['withdrawal_total'] += withdrawal
    group_totals[key]['deposit_total'] += deposit


def summarize_by_period(data):
    month_stats = defaultdict(lambda: {
        'withdrawal_total': 0.0,
        'deposit_total': 0.0,
    })
    week_stats = defaultdict(lambda: {
        'withdrawal_total': 0.0,
        'deposit_total': 0.0,
    })
    day_stats = defaultdict(lambda: {
        'withdrawal_total': 0.0,
        'deposit_total': 0.0,
    })

    skipped_dates = 0
    for entry in data:
        parsed_date = parse_date(entry['date'])
        if parsed_date is None:
            skipped_dates += 1
            continue

        iso_year, iso_week, _ = parsed_date.isocalendar()
        month_key = parsed_date.strftime("%Y-%m")
        week_key = f"{iso_year}-W{iso_week:02d}"
        day_key = parsed_date.isoformat()

        update_group_totals(month_stats, month_key, entry['withdrawal'], entry['deposit'])
        update_group_totals(week_stats, week_key, entry['withdrawal'], entry['deposit'])
        update_group_totals(day_stats, day_key, entry['withdrawal'], entry['deposit'])

    return month_stats, week_stats, day_stats, skipped_dates


def average_period_totals(stats):
    period_count = len(stats)
    withdrawal_total_sum = sum(values['withdrawal_total'] for values in stats.values())
    deposit_total_sum = sum(values['deposit_total'] for values in stats.values())
    return (
        average(withdrawal_total_sum, period_count),
        average(deposit_total_sum, period_count)
    )


def print_average_totals(month_stats, week_stats, day_stats, skipped_dates):
    avg_month_withdrawal, avg_month_deposit = average_period_totals(month_stats)
    avg_week_withdrawal, avg_week_deposit = average_period_totals(week_stats)
    avg_day_withdrawal, avg_day_deposit = average_period_totals(day_stats)

    print("\nOverall Average Totals")
    print("----------------------")
    print(f"Per month: avg total withdrawal = ${avg_month_withdrawal:.2f}, avg total deposit = ${avg_month_deposit:.2f}")
    print(f"Per week:  avg total withdrawal = ${avg_week_withdrawal:.2f}, avg total deposit = ${avg_week_deposit:.2f}")
    print(f"Per day:   avg total withdrawal = ${avg_day_withdrawal:.2f}, avg total deposit = ${avg_day_deposit:.2f}")

    if skipped_dates:
        print(f"\nSkipped {skipped_dates} row(s) due to unrecognized date format.")


def plot_combined_chart(day_stats):
    dates = sorted(day_stats.keys())
    balances = [day_stats[date]['deposit_total'] - day_stats[date]['withdrawal_total'] for date in dates]
    withdrawals = [day_stats[date]['withdrawal_total'] for date in dates]
    deposits = [day_stats[date]['deposit_total'] for date in dates]

    x = list(range(len(dates)))
    width = 0.4

    fig, ax1 = plt.subplots(figsize=(12, 6))
    bars_withdrawals = ax1.bar(
        [i - width / 2 for i in x],
        withdrawals,
        width,
        label='Withdrawals',
        color='red',
        alpha=0.7,
    )
    bars_deposits = ax1.bar(
        [i + width / 2 for i in x],
        deposits,
        width,
        label='Deposits',
        color='green',
        alpha=0.7,
    )
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Withdrawal/Deposit Totals ($)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=45, ha='right')

    ax2 = ax1.twinx()
    line_balance, = ax2.plot(
        x,
        balances,
        marker='o',
        linestyle='-',
        color='blue',
        linewidth=2,
        label='Net Balance Trend',
    )
    ax2.set_ylabel('Net Balance Trend ($)')

    plt.title('Withdrawals, Deposits, and Net Balance Trend Over Time')
    handles = [bars_withdrawals, bars_deposits, line_balance]
    labels = [handle.get_label() for handle in handles]
    ax1.legend(handles, labels, loc='upper left')
    plt.tight_layout()
    plt.show()


def main():
    file_path = select_csv_file()
    if not file_path:
        raise SystemExit("No file selected.")

    indexes, has_headers = get_column_indexes(file_path)

    print(f"Date index: {indexes['date']}")
    print(f"Description index: {indexes['description']}")
    print(f"Withdrawal index: {indexes['withdrawal']}")
    print(f"Deposit index: {indexes['deposit']}")
    print(f"Balance index: {indexes['balance']}")

    data = load_data(file_path, indexes, has_headers)
    month_stats, week_stats, day_stats, skipped_dates = summarize_by_period(data)

    print_average_totals(month_stats, week_stats, day_stats, skipped_dates)
    plot_combined_chart(day_stats)


if __name__ == '__main__':
    main()