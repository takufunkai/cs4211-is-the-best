import re
import csv

with open('out.txt', 'r') as file:
    data = file.read()

# Regex to get required data
pattern = r'(\d{4}-\d{2}-\d{2})_(.+?)_(.+?)_[RL]H-[RL]H\.pcsp.*?Probability \[\s*(\d+\.\d+),\s*(\d+\.\d+)\s*\];'

# Find all matches in data string
matches = re.findall(pattern, data, re.DOTALL)

# Create CSV file
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow(['date', 'P1Name', 'P2Name', 'P1WinProb', 'P2WinProb'])

    # Write extracted data
    for match in matches:
        date, p1_name, p2_name, prob1, prob2 = match
        p1_win_prob = (float(prob1) + float(prob2)) / 2
        p2_win_prob = 1 - p1_win_prob
        writer.writerow([date, p1_name.replace(
            '-', ' '), p2_name.replace('-', ' '), f'{p1_win_prob:.4f}', f'{p2_win_prob:.4f}'])

print('Data parsed successfully')
