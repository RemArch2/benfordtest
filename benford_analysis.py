import pandas as pd
import matplotlib.pyplot as plt
import os
import math

def get_first_digit(n):
    try:
        # Handle NA or non-numeric
        if pd.isna(n):
            return None

        n_abs = abs(n)
        if n_abs == 0:
            return None

        # Convert to string to find the first non-zero digit
        # This handles floats like 0.0045 -> first digit 4
        # And ints like 123 -> first digit 1
        # Use format to avoid scientific notation 1e-05 etc
        s = "{:.15f}".format(n_abs)
        s = s.replace('.', '').lstrip('0')

        if not s:
            return None

        return int(s[0])
    except Exception as e:
        return None

def main():
    print("Starting Benford's Law Analysis...")

    # Create output directory
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Load data
    file_path = 'je_samples.xlsx'
    try:
        df = pd.read_excel(file_path)
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return

    # Check for Amount column
    process_column = None
    if 'Amount' in df.columns:
        process_column = 'Amount'
    elif 'AbsoluteAmount' in df.columns:
        print("Column 'Amount' not found. Using 'AbsoluteAmount' instead.")
        process_column = 'AbsoluteAmount'
    else:
        print("Error: Neither 'Amount' nor 'AbsoluteAmount' column found in Excel file.")
        print(f"Available columns: {df.columns.tolist()}")
        return

    # Extract first digits
    print(f"Processing column: {process_column}")
    first_digits = df[process_column].apply(get_first_digit)

    # Filter out None values
    first_digits = first_digits.dropna()

    if first_digits.empty:
        print("No valid numeric data found for analysis.")
        return

    total_count = len(first_digits)
    print(f"Total valid entries: {total_count}")

    # Calculate frequencies
    digit_counts = first_digits.value_counts().sort_index()

    # Ensure all digits 1-9 are present in index
    for i in range(1, 10):
        if i not in digit_counts.index:
            digit_counts[i] = 0

    digit_counts = digit_counts.sort_index()
    actual_freq = digit_counts / total_count

    # Calculate Benford's expected frequencies
    benford_freq = {d: math.log10(1 + 1/d) for d in range(1, 10)}

    # Generate Report
    report_path = os.path.join(output_dir, 'benford_analysis_report.txt')
    with open(report_path, 'w') as f:
        f.write("Benford's Law Analysis Report\n")
        f.write("=============================\n\n")
        f.write(f"Analyzed File: {file_path}\n")
        f.write(f"Column Analyzed: {process_column}\n")
        f.write(f"Total Valid Entries: {total_count}\n\n")
        f.write(f"{'Digit':<6} | {'Count':<10} | {'Actual %':<10} | {'Benford %':<10} | {'Diff %':<10}\n")
        f.write("-" * 55 + "\n")

        for d in range(1, 10):
            count = int(digit_counts[d])
            act_p = actual_freq[d] * 100
            ben_p = benford_freq[d] * 100
            diff = act_p - ben_p
            f.write(f"{d:<6} | {count:<10} | {act_p:<10.2f} | {ben_p:<10.2f} | {diff:<10.2f}\n")

    print(f"Report saved to {report_path}")

    # Generate Chart
    plt.figure(figsize=(10, 6))
    digits = list(range(1, 10))
    actual_values = [actual_freq[d] * 100 for d in digits]
    benford_values = [benford_freq[d] * 100 for d in digits]

    bar_width = 0.35
    index = range(len(digits))

    plt.bar([i - bar_width/2 for i in index], actual_values, bar_width, label='Actual')
    plt.bar([i + bar_width/2 for i in index], benford_values, bar_width, label='Benford Expected', alpha=0.7)

    plt.xlabel('Leading Digit')
    plt.ylabel('Frequency (%)')
    plt.title("Benford's Law Analysis: Actual vs Expected Distribution")
    plt.xticks(index, digits)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    chart_path = os.path.join(output_dir, 'benford_analysis_chart.png')
    plt.savefig(chart_path)
    print(f"Chart saved to {chart_path}")

if __name__ == "__main__":
    main()
