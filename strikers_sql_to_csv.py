import re
import csv
from io import StringIO
import csv


def split_sql_values(value_str):
    cleaned = value_str.replace('\n', ' ').replace("''", "'")

    fake_csv = StringIO(cleaned)
    reader = csv.reader(fake_csv, quotechar="'", delimiter=',', escapechar='\\', skipinitialspace=True)

    return [part.strip() for part in next(reader)]


def transform_insert_line(sql):
    if not sql.strip().lower().startswith("insert into player_stats"):
        print("[DEBUG] Skipped: Not an insert into player_stats statement.")
        return None

    values_match = re.search(r"VALUES\s*\((.*)\)\s*;", sql, re.DOTALL | re.IGNORECASE)

    if not values_match:
        print("[DEBUG] No VALUES found in statement.")
        return None

    raw_values = values_match.group(1).strip()
    parts = split_sql_values(raw_values)

    if len(parts) != 29:
        print(f"[ERROR] Expected 29 values but found {len(parts)}. Skipping line.")
        return None

    try:
        name = parts[0].strip("'")
        position = parts[1].strip("'")
        club = parts[2].strip("'")
        nationality = parts[3].strip("'")
        height_cm = float(parts[4])
        weight_kg = float(parts[5])
        preferred_foot = parts[6].strip("'")
        age = int(parts[7])
        appearances = int(parts[8])
        subs = int(parts[9])
        starts = int(parts[10])
        minutes_played = int(parts[11])
        goals = int(parts[12])
        shots = int(parts[13])
        shots_on_target = int(parts[14])
        assists = int(parts[15])
        key_passes = int(parts[16])
        passes_completed = int(parts[17])
        market_value_min = int(parts[18])
        market_value_max = int(parts[19])
        dribbles_made = int(parts[20])
        goals_per_90 = float(parts[21])
        shots_on_target_per_90 = float(parts[22])
        assists_per_90 = float(parts[23])
        key_passes_per_90 = float(parts[24])
        passes_completed_per_90 = float(parts[25])
        conversion_rate = float(parts[26])
        shot_accuracy = float(parts[27])
        goal_involvement_per_90 = float(parts[28])

        return [
            name, position, club, nationality, height_cm, weight_kg, preferred_foot, age,
            appearances, subs, starts, minutes_played, goals, shots, shots_on_target,
            assists, key_passes, passes_completed, market_value_min, market_value_max,
            dribbles_made, goals_per_90, shots_on_target_per_90, assists_per_90,
            key_passes_per_90, passes_completed_per_90, conversion_rate, shot_accuracy,
            goal_involvement_per_90
        ]

    except Exception as e:
        print(f"[ERROR] Exception while parsing: {e}")
        return None


def process_sql_file_to_csv(input_path, output_path):
    header = [
        "name", "position", "club", "nationality", "height_cm", "weight_kg", "preferred_foot", "age",
        "appearances", "subs", "starts", "minutes_played", "goals", "shots", "shots_on_target",
        "assists", "key_passes", "passes_completed", "market_value_min", "market_value_max",
        "dribbles_made", "goals_per_90", "shots_on_target_per_90", "assists_per_90",
        "key_passes_per_90", "passes_completed_per_90", "conversion_rate", "shot_accuracy",
        "goal_involvement_per_90"
    ]

    with open(input_path, 'r', encoding='utf-8') as infile, \
            open(output_path, 'w', newline='', encoding='utf-8') as outfile:

        writer = csv.writer(outfile)
        writer.writerow(header)

        statement_lines = []

        for line_num, line in enumerate(infile, start=1):
            statement_lines.append(line.rstrip())
            if line.strip().endswith(');'):
                full_stmt = ' '.join(statement_lines)
                row = transform_insert_line(full_stmt)
                if row:
                    writer.writerow(row)
                    print(f"[DEBUG] Parsed and wrote row ending at line {line_num}")
                else:
                    print(f"[DEBUG] Failed to parse or skipped row ending at line {line_num}")
                statement_lines = []


if __name__ == "__main__":

    input_path = r"C:\Users\ijordan\Desktop\BORRAR\processed_strikers.sql"
    output_path = r"C:\Users\ijordan\Desktop\BORRAR\strikers.csv"

    process_sql_file_to_csv(input_path, output_path)