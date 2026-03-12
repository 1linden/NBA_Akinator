import sys
import os
import time
import pandas as pd
from datetime import date, datetime
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playerawards, playercareerstats


OUTPUT_CSV = "active_nba_players.csv"
SLEEP_SECONDS = 1.5
BATCH_SIZE = 10


OUTPUT_COLUMNS = [
    "player_name",
    "team",
    "age",
    "draft_year",
    "draft_pick_number",
    "position",
    "made_all_star",
    "made_all_nba",
    "made_all_defence",
    "won_dpoy",
    "won_mvp",
    "played_in_playoffs",
    "num_championships",
    "ppg_career_high",
    "apg_career_high",
    "rpg_career_high",
]


def age_in_years_no_decimal(birthdate_str: str) -> int | None:
    if not birthdate_str or pd.isna(birthdate_str):
        return None

    try:
        birthdate = datetime.fromisoformat(str(birthdate_str).replace("Z", "")).date()
    except ValueError:
        return None

    today = date.today()
    age = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age


def safe_str(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value if value else None


def safe_int(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def get_primary_position(position_str):
    """
    Convert API positions like 'F-C' or 'G-F' to a single full-word position.
    """
    if pd.isna(position_str):
        return None

    pos = str(position_str).strip()
    if "-" in pos:
        pos = pos.split("-")[0]

    mapping = {
        "G": "Guard",
        "F": "Forward",
        "C": "Center",
        "Guard": "Guard",
        "Forward": "Forward",
        "Center": "Center",
    }
    return mapping.get(pos, pos)


def normalize_award_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower()


def extract_award_stats(player_id: int) -> dict:
    """
    Build:
    - made_all_star (0/1)
    - num_championships (count)
    - won_mvp (0/1)
    - won_dpoy (0/1)
    - made_all_nba (0/1)
    - made_all_defence (0/1)
    """
    awards_df = playerawards.PlayerAwards(player_id=player_id).get_data_frames()[0]

    if awards_df.empty:
        return {
            "made_all_star": 0,
            "num_championships": 0,
            "won_mvp": 0,
            "won_dpoy": 0,
            "made_all_nba": 0,
            "made_all_defence": 0,
        }

    descriptions = normalize_award_text(awards_df["DESCRIPTION"])

    made_all_star = int(descriptions.eq("nba all-star").any())
    num_championships = int(descriptions.eq("nba champion").sum())
    won_mvp = int(descriptions.eq("nba most valuable player").any())
    won_dpoy = int(descriptions.eq("nba defensive player of the year").any())

    # Broader matching is safer here because award descriptions can vary by team number
    # (e.g., first/second/third team).
    made_all_nba = int(descriptions.str.contains("all-nba", na=False).any())
    made_all_defence = int(
        descriptions.str.contains("all-defensive", na=False).any()
        or descriptions.str.contains("all defense", na=False).any()
    )

    return {
        "made_all_star": made_all_star,
        "num_championships": num_championships,
        "won_mvp": won_mvp,
        "won_dpoy": won_dpoy,
        "made_all_nba": made_all_nba,
        "made_all_defence": made_all_defence,
    }


def _collapse_to_one_row_per_season(df: pd.DataFrame) -> pd.DataFrame:
    """
    PlayerCareerStats can include more than one row in a season if a player was traded.
    Keep the row with the largest GP for each season, which usually preserves the
    season-total row when one exists and avoids small-sample team-split spikes.
    """
    if df.empty:
        return df

    df = df.copy()
    df["GP"] = pd.to_numeric(df["GP"], errors="coerce").fillna(0)
    df = df.sort_values(["SEASON_ID", "GP"], ascending=[True, False])
    df = df.drop_duplicates(subset="SEASON_ID", keep="first")
    return df


def extract_career_stats(player_id: int) -> dict:
    """
    Returns:
    - ppg_career_high: max regular-season PTS per game over seasons
    - apg_career_high: max regular-season AST per game over seasons
    - rpg_career_high: max regular-season REB per game over seasons
    - played_in_playoffs: 1 if postseason MIN per game > 0 in any season, else 0
    """
    career = playercareerstats.PlayerCareerStats(
        player_id=player_id,
        per_mode36="PerGame",
    )

    reg_df = career.season_totals_regular_season.get_data_frame()
    post_df = career.season_totals_post_season.get_data_frame()

    ppg_career_high = None
    apg_career_high = None
    rpg_career_high = None
    played_in_playoffs = 0

    if not reg_df.empty:
        reg_df = _collapse_to_one_row_per_season(reg_df)

        reg_df["PTS"] = pd.to_numeric(reg_df["PTS"], errors="coerce")
        reg_df["AST"] = pd.to_numeric(reg_df["AST"], errors="coerce")
        reg_df["REB"] = pd.to_numeric(reg_df["REB"], errors="coerce")

        ppg_career_high = reg_df["PTS"].max()
        apg_career_high = reg_df["AST"].max()
        rpg_career_high = reg_df["REB"].max()

        if pd.isna(ppg_career_high):
            ppg_career_high = None
        else:
            ppg_career_high = round(float(ppg_career_high), 1)

        if pd.isna(apg_career_high):
            apg_career_high = None
        else:
            apg_career_high = round(float(apg_career_high), 1)

        if pd.isna(rpg_career_high):
            rpg_career_high = None
        else:
            rpg_career_high = round(float(rpg_career_high), 1)

    if not post_df.empty:
        post_df = _collapse_to_one_row_per_season(post_df)
        post_df["MIN"] = pd.to_numeric(post_df["MIN"], errors="coerce").fillna(0)
        played_in_playoffs = int((post_df["MIN"] > 0).any())

    return {
        "ppg_career_high": ppg_career_high,
        "apg_career_high": apg_career_high,
        "rpg_career_high": rpg_career_high,
        "played_in_playoffs": played_in_playoffs,
    }


def extract_player_row(player_id: int, full_name: str) -> dict | None:
    """
    Pull:
    - CommonPlayerInfo
    - PlayerAwards
    - PlayerCareerStats

    Return None if the player currently has no team.
    """
    info_df = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_data_frames()[0]

    if info_df.empty:
        return None

    row = info_df.iloc[0]

    team = safe_str(row.get("TEAM_NAME"))
    if not team:
        # Skip players with no current team
        return None

    draft_pick = safe_int(row.get("DRAFT_NUMBER"))
    if draft_pick is None:
        draft_pick = 61

    draft_year = safe_int(row.get("DRAFT_YEAR"))

    awards = extract_award_stats(player_id)
    career = extract_career_stats(player_id)

    player_row = {
        "player_name": full_name,
        "draft_pick_number": draft_pick,
        "draft_year": draft_year,
        "position": get_primary_position(row.get("POSITION")),
        "team": team,
        "age": age_in_years_no_decimal(row.get("BIRTHDATE")),
        "made_all_star": awards["made_all_star"],
        "num_championships": awards["num_championships"],
        "won_mvp": awards["won_mvp"],
        "won_dpoy": awards["won_dpoy"],
        "made_all_nba": awards["made_all_nba"],
        "made_all_defence": awards["made_all_defence"],
        "ppg_career_high": career["ppg_career_high"],
        "apg_career_high": career["apg_career_high"],
        "rpg_career_high": career["rpg_career_high"],
        "played_in_playoffs": career["played_in_playoffs"],
    }

    return player_row


def save_rows(rows: list[dict]) -> None:
    if os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0:
        existing_df = pd.read_csv(OUTPUT_CSV)
    else:
        existing_df = pd.DataFrame(columns=OUTPUT_COLUMNS)

    new_df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=OUTPUT_COLUMNS)

    for col in OUTPUT_COLUMNS:
        if col not in existing_df.columns:
            existing_df[col] = None
        if col not in new_df.columns:
            new_df[col] = None

    frames = []
    if not existing_df.empty:
        frames.append(existing_df)
    if not new_df.empty:
        frames.append(new_df)

    if frames:
        combined_df = pd.concat(frames, ignore_index=True)
    else:
        combined_df = pd.DataFrame(columns=OUTPUT_COLUMNS)

    if "player_name" in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset="player_name", keep="last")

    combined_df = combined_df[OUTPUT_COLUMNS]
    combined_df.to_csv(OUTPUT_CSV, index=False)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"1", "2", "3", "4"}:
        return

    part = int(sys.argv[1])

    if (os.path.exists(OUTPUT_CSV)) and (part == 1): 
        with open(OUTPUT_CSV, "w"): 
            pass 

    active_players = players.get_active_players()
    total = len(active_players)

    if part == 1:
        start_index = 0
        end_index = 150
    elif part == 2:
        start_index = 150
        end_index = 300
    elif part == 3:
        start_index = 300
        end_index = 450
    else:
        start_index = 450
        end_index = total

    rows = []

    for batch_start in range(start_index, end_index, BATCH_SIZE):
        batch_players = active_players[batch_start: min(batch_start + BATCH_SIZE, end_index)]

        for j, p in enumerate(batch_players, start=batch_start + 1):
            player_id = p["id"]
            full_name = p["full_name"]

            try:
                print(f"[{j}/{total}] Fetching {full_name} ({player_id})")
                row = extract_player_row(player_id, full_name)

                if row is None:
                    print(f"  Skipping {full_name}: no current team")
                    continue

                rows.append(row)

            except Exception as e:
                print(f"  Failed for {full_name}: {e}")
                continue

            time.sleep(SLEEP_SECONDS)

        save_rows(rows)
        print(f"Players {batch_start + 1} - {batch_start + len(batch_players)} saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()