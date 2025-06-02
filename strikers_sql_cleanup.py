import re
import csv
from io import StringIO


def split_sql_values(value_str):
    cleaned = value_str.replace("''", "'")

    fake_csv = StringIO(cleaned)
    reader = csv.reader(fake_csv, quotechar="'", delimiter=',', escapechar='\\', skipinitialspace=True)

    return [part.strip() for part in next(reader)]


def parse_market_value(value_str):
    """Parses a market value string like '$5.8M - $7.6M', '$500k', or '$500.356'."""

    def parse_single(val):
        val = val.strip().replace('$', '')

        if 'M' in val:
            return float(val.replace('M', '')) * 1_000_000
        elif 'K' in val:
            return float(val.replace('K', '')) * 1_000
        else:
            return float(val)

    if '-' in value_str:
        parts = value_str.split('-')
        min_val = parse_single(parts[0].strip())
        max_val = parse_single(parts[1].strip())
        return int(min_val), int(max_val)
    else:
        val = parse_single(value_str)
        return int(val), int(val)


def convert_height(height_str):
    match = re.match(r"(\d+)'(\d+)\"", height_str)

    if match:
        feet = int(match.group(1))
        inches = int(match.group(2))
        return round((feet * 12 + inches) * 2.54, 2)

    match2 = re.match(r"(\d{1})(\d{2})\"?", height_str)
    if match2:
        feet = int(match2.group(1))
        inches = int(match2.group(2))
        return round((feet * 12 + inches) * 2.54, 2)

    return 0.0


def parse_appearances(appearance_str):
    match = re.match(r"(\d+)", appearance_str)

    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Cannot parse appearances: {appearance_str}")


def convert_weight(weight_str):
    """Convert weight from '152 lbs' to kilograms."""

    match = re.match(r"(\d+)\s*lbs", weight_str)

    if match:
        pounds = int(match.group(1))
        return round(pounds * 0.453592, 2)
    return 0.0


def transform_insert_line(line):
    if not line.strip().lower().startswith("insert into players"):
        return None

    print(f"[DEBUG] Processing line:\n{line.strip()}")
    values = re.findall(r"VALUES\s*\((.*?)\);", line, re.DOTALL)

    if not values:
        print("[DEBUG] No VALUES() found.")
        return None

    raw_values = values[0]

    print(f"[DEBUG] Raw values string:\n{raw_values}\n")

    parts = split_sql_values(raw_values)

    print(f"[DEBUG] Parsed {len(parts)} values:")

    for i, part in enumerate(parts):
        print(f"  [{i}] -> {part}")

    if len(parts) != 29:
        print(f"[ERROR] Skipping malformed line: Expected 29 parts, got {len(parts)}.")
        return None

    try:
        name = parts[0].strip("'")
        position = parts[1].strip("'")
        club = parts[2].strip("'")
        nationality = parts[3].strip("'")
        height_cm = convert_height(parts[4].strip("'"))
        weight_kg = convert_weight(parts[5].strip("'"))
        preferred_foot = parts[6].strip("'")
        age = int(parts[7])
        appearances = parse_appearances(parts[8].strip("'"))
        starts = int(parts[9])
        subs = appearances - starts
        minutes_played = int(parts[10])
        goals = int(parts[11])
        shots = int(parts[12])
        shots_on_target = int(parts[13])
        assists = int(parts[14])
        key_passes = int(parts[15])
        passes_completed = int(parts[16])
        mv_min, mv_max = parse_market_value(parts[17].strip("'"))
        dribbles_made = int(parts[18])
        goals_per_90 = float(parts[19])
        shots_on_target_per_90 = float(parts[20])
        assists_per_90 = float(parts[21])
        key_passes_per_90 = float(parts[22])
        passes_completed_per_90 = float(parts[23])
        conversion_rate = float(parts[24])
        shot_accuracy = float(parts[25])
        goal_involvement_per_90 = float(parts[26])
        normalized_rating = float(parts[28])

        return f"""INSERT INTO player_stats (
    name, position, club, nationality, height_cm, weight_kg, preferred_foot, age,
    appearances, subs, starts, minutes_played, goals, shots, shots_on_target,
    assists, key_passes, passes_completed, market_value_min, market_value_max,
    dribbles_made, goals_per_90, shots_on_target_per_90, assists_per_90,
    key_passes_per_90, passes_completed_per_90, conversion_rate, shot_accuracy,
    goal_involvement_per_90
) VALUES (
    '{name}', '{position}', '{club}', '{nationality}', {height_cm}, {weight_kg}, '{preferred_foot}', {age},
    {appearances}, {subs}, {starts}, {minutes_played}, {goals}, {shots}, {shots_on_target},
    {assists}, {key_passes}, {passes_completed}, {mv_min}, {mv_max},
    {dribbles_made}, {goals_per_90}, {shots_on_target_per_90}, {assists_per_90},
    {key_passes_per_90}, {passes_completed_per_90}, {conversion_rate}, {shot_accuracy},
    {goal_involvement_per_90}
);"""

    except Exception as e:
        print(f"[ERROR] Failed to parse line: {e}")
        return None


def process_sql_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            transformed = transform_insert_line(line)
            if transformed:
                outfile.write(transformed + '\n')


if __name__ == "__main__":

    input_path = r"C:\Users\ijordan\Desktop\BORRAR\insert_all_strikers.sql"
    output_path = r"C:\Users\ijordan\Desktop\BORRAR\processed_strikers.sql"

    process_sql_file(input_path, output_path)