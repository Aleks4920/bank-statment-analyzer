
import tkinter as tk
from tkinter import filedialog
import csv
from datetime import datetime
from collections import defaultdict


# open up file select to allow user to select a .csv file to read in
root = tk.Tk()
root.withdraw()  # Hide the main window
file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

if not file_path:
    raise SystemExit("No file selected.")


# files may come in with headings or not so we will need to find the columns we want, we want date, description, withdrawal, deposit, and balance. We will read in the first line of the file to find the column indexes for these fields
# if the file has headings, we will use those to find the indexes, if not we will assume the order is date, description, withdrawal, deposit, balance
with open(file_path, 'r') as f:
    reader = csv.reader(f)
    first_row = next(reader, [])
    columns = [col.strip().strip('"').lower() for col in first_row]
    if 'date' in columns and 'description' in columns and 'withdrawal' in columns and 'deposit' in columns and 'balance' in columns:
        date_index = columns.index('date')
        description_index = columns.index('description')
        withdrawal_index = columns.index('withdrawal')
        deposit_index = columns.index('deposit')
        balance_index = columns.index('balance')
    else:
        date_index = 0
        description_index = 1
        withdrawal_index = 2
        deposit_index = 3
        balance_index = 4

# print out the indexes we found for each column
print(f"Date index: {date_index}")
print(f"Description index: {description_index}")
print(f"Withdrawal index: {withdrawal_index}")
print(f"Deposit index: {deposit_index}")
print(f"Balance index: {balance_index}")

def parse_amount(value):
    cleaned = value.strip().strip('"').replace('$', '').replace(',', '')
    return float(cleaned) if cleaned else 0.0


# convert the columns found as python types, we will read in the file again and convert the columns to the appropriate types, we will store the data in a list of dictionaries, where each dictionary represents a row in the file
data = []
with open(file_path, 'r') as f:
    reader = csv.reader(f)
    # skip the first line if it has headings
    if 'date' in columns and 'description' in columns and 'withdrawal' in columns and 'deposit' in columns and 'balance' in columns:
        next(reader, None)
    for row in reader:
        if not row:  # Skip empty lines
            continue
        date = row[date_index]
        description = row[description_index]
        withdrawal = parse_amount(row[withdrawal_index]) if withdrawal_index < len(row) else 0.0
        deposit = parse_amount(row[deposit_index]) if deposit_index < len(row) else 0.0
        balance = parse_amount(row[balance_index]) if balance_index < len(row) else 0.0
        data.append({
            'date': date,
            'description': description,
            'withdrawal': withdrawal,
            'deposit': deposit,
            'balance': balance
        })

# return the average withdrawal and deposit amounts, by month, week, and by day to see average spending habits, we will use the date column to group the data by month, week, and day
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


def update_group_totals(group_totals, key, withdrawal, deposit):
    group_totals[key]['withdrawal_total'] += withdrawal
    group_totals[key]['deposit_total'] += deposit


month_stats = defaultdict(lambda: {
    'withdrawal_total': 0.0,
    'deposit_total': 0.0
})

week_stats = defaultdict(lambda: {
    'withdrawal_total': 0.0,
    'deposit_total': 0.0
})

day_stats = defaultdict(lambda: {
    'withdrawal_total': 0.0,
    'deposit_total': 0.0
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


def average_period_totals(stats):
    period_count = len(stats)
    withdrawal_total_sum = sum(values['withdrawal_total'] for values in stats.values())
    deposit_total_sum = sum(values['deposit_total'] for values in stats.values())
    return (
        average(withdrawal_total_sum, period_count),
        average(deposit_total_sum, period_count)
    )


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



# create a graph represnting the trends seen with a line showing the balance over time, and a bar graph showing the total withdrawals and deposits over time, we will use matplotlib to create the graphs
import matplotlib.pyplot as plt

# Prepare data for the line graph (balance over time)
dates = list(day_stats.keys())
balances = [day_stats[date]['deposit_total'] - day_stats[date]['withdrawal_total'] for date in dates]

# Prepare data for the bar graph (total withdrawals and deposits)
withdrawals = [day_stats[date]['withdrawal_total'] for date in dates]
deposits = [day_stats[date]['deposit_total'] for date in dates]

# Create the line graph
plt.figure(figsize=(10, 5))
plt.plot(dates, balances, marker='o', linestyle='-', color='blue')
plt.title('Balance Over Time')
plt.xlabel('Date')
plt.ylabel('Balance')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Create the bar graph
x = range(len(dates))
width = 0.35

plt.figure(figsize=(10, 5))
plt.bar([i - width/2 for i in x], withdrawals, width, label='Withdrawals', color='red')
plt.bar([i + width/2 for i in x], deposits, width, label='Deposits', color='green')
plt.title('Total Withdrawals and Deposits Over Time')
plt.xlabel('Date')
plt.ylabel('Amount')
plt.xticks(x, dates, rotation=45)
plt.legend()
plt.tight_layout()
plt.show()