import re

def preprocess_line(line):
    return re.sub(r"(?<=')(\d)\'(\d{1,2})\"", r"\1''\2\"", line)

def split_sql_values(value_str):
    result = []
    current = ''
    inside_quotes = False
    i = 0
    while i < len(value_str):
        char = value_str[i]
        if char == "'":
            if inside_quotes and i + 1 < len(value_str) and value_str[i + 1] == "'":
                current += "'"
                i += 1
            else:
                inside_quotes = not inside_quotes
        elif char == ',' and not inside_quotes:
            result.append(current.strip())
            current = ''
        else:
            current += char
        i += 1
    if current:
        result.append(current.strip())
    return result

def parse_market_value(value_str, line_number, player_name="Unknown"):
    if "not for sale" in value_str.lower():
        return 0, 0

    def parse_single(val):

        val = val.strip().replace('$', '').upper()
        match = re.match(r"([\d.]+)([MK]?)", val)
        if not match:
            return 0.0
        number = safe_float(match.group(1), line_number, "MarketValue", player_name)
        suffix = match.group(2)
        if suffix == 'M':
            return number * 1_000_000
        elif suffix == 'K':
            return number * 1_000
        return number

    try:
        if '-' in value_str:
            parts = value_str.split('-')
            return int(parse_single(parts[0])), int(parse_single(parts[1]))
        else:
            val = parse_single(value_str)
            return int(val), int(val)
    except:
        return 0, 0

def convert_height(height_str):
    height_str = height_str.strip().lower()
    match = re.match(r"(\d+)'(\d+)", height_str)

    if match:
        feet = int(match.group(1))
        inches = int(match.group(2))
        return round((feet * 12 + inches) * 2.54, 2)
    match2 = re.match(r"(\d{1})(\d{2})$", height_str)

    if match2:
        feet = int(match2.group(1))
        inches = int(match2.group(2))
        return round((feet * 12 + inches) * 2.54, 2)
    match3 = re.match(r"(\d+)\s*cm", height_str)

    if match3:
        return float(match3.group(1))
    if height_str.isdigit():
        return float(height_str)
    return 0.0

def parse_appearances(appearance_str):
    match = re.match(r"(\d+)", appearance_str)
    if match:
        return int(match.group(1))
    else:
        return 0

def convert_weight(weight_str):

    match = re.match(r"(\d+)\s*lbs", weight_str)
    if match:
        return round(int(match.group(1)) * 0.453592, 2)
    return 0.0

def safe_float(value_str, line_number, field_name, player_name="Unknown"):
    try:
        raw = str(value_str).strip()
        cleaned = raw.strip("'\"").strip().lower()
        if cleaned in ("unknown", "null", "none", ""):
            return 0.0
        return float(cleaned)
    except:
        return 0.0

def transform_insert_line(line, line_number):

    if not line.strip().lower().startswith("insert into players"):
        return None

    line = preprocess_line(line)
    match = re.search(r"values\s*\((.*)\)\s*;", line.strip(), re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    raw_values = match.group(1)
    parts = split_sql_values(raw_values)

    if len(parts) != 29:
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
        mv_min, mv_max = parse_market_value(parts[17].strip("'"), line_number, name)
        dribbles_made = int(parts[18])
        goals_per_90 = safe_float(parts[19], line_number, "GoalsPer90", name)
        shots_on_target_per_90 = safe_float(parts[20], line_number, "ShotsOnTargetPer90", name)
        assists_per_90 = safe_float(parts[21], line_number, "AssistsPer90", name)
        key_passes_per_90 = safe_float(parts[22], line_number, "KeyPassesPer90", name)
        passes_completed_per_90 = safe_float(parts[23], line_number, "PassesCompletedPer90", name)
        conversion_rate = safe_float(parts[24], line_number, "ConversionRate", name)
        shot_accuracy = safe_float(parts[25], line_number, "ShotAccuracy", name)
        goal_involvement_per_90 = safe_float(parts[26], line_number, "GoalInvolvementPer90", name)
        rating = safe_float(parts[27], line_number, "Rating", name)
        normalized_rating = safe_float(parts[28], line_number, "NormalizedRating", name)

        return f"""INSERT INTO player_stats (
    Name, Position, Club, Nationality, HeightCm, WeightKg, PreferredFoot, Age,
    Appearances, Subs, Starts, MinutesPlayed, Goals, Shots, ShotsOnTarget,
    Assists, KeyPasses, PassesCompleted, MarketValueMin, MarketValueMax,
    DribblesMade, GoalsPer90, ShotsOnTargetPer90, AssistsPer90,
    KeyPassesPer90, PassesCompletedPer90, ConversionRate, ShotAccuracy,
    GoalInvolvementPer90
) VALUES (
    '{name}', '{position}', '{club}', '{nationality}', {height_cm}, {weight_kg}, '{preferred_foot}', {age},
    {appearances}, {subs}, {starts}, {minutes_played}, {goals}, {shots}, {shots_on_target},
    {assists}, {key_passes}, {passes_completed}, {mv_min}, {mv_max},
    {dribbles_made}, {goals_per_90}, {shots_on_target_per_90}, {assists_per_90},
    {key_passes_per_90}, {passes_completed_per_90}, {conversion_rate}, {shot_accuracy},
    {goal_involvement_per_90}
);"""
    except:
        return None

def process_sql_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line_number, line in enumerate(infile, start=1):
            transformed = transform_insert_line(line, line_number)
            if transformed:
                outfile.write(transformed + '\n')

if __name__ == "__main__":

    input_path = r"C:\Users\Isaac\Desktop\Programacion\PyScripts\insert_all_strikers.sql"
    output_path = r"C:\Users\Isaac\Desktop\Programacion\PyScripts\processed_strikers.sql"

    process_sql_file(input_path, output_path)
