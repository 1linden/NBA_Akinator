"""
questions.py

Each question has:
- an id
- the text shown to the user
- a rule type
- optional extra value(s)
- optional dependency rules

The engine will use these definitions to test each player row.
"""

QUESTIONS = [
    {
        "id": "drafted_top_10",
        "text": "Was the player drafted top 10?",
        "type": "draft_range",
        "min": 1,
        "max": 10,
    },
    {
        "id": "drafted_bottom_10",
        "text": "Was the player drafted with pick 50 or later?",
        "type": "draft_range",
        "min": 50,
        "max": 60,
    },
    {
        "id": "drafted_first_round",
        "text": "Was the player drafted in the first round?",
        "type": "draft_range",
        "min": 1,
        "max": 30,
    },
    {
        "id": "drafted_second_round",
        "text": "Was the player drafted in the second round?",
        "type": "draft_range",
        "min": 31,
        "max": 60,
    },
    {
        "id": "undrafted",
        "text": "Was the player undrafted?",
        "type": "draft_exact",
        "value": 61,
    },
    {
        "id": "position_guard",
        "text": "Does the player primarily play Guard?",
        "type": "position_is",
        "value": "Guard",
    },
    {
        "id": "position_forward",
        "text": "Does the player primarily play Forward?",
        "type": "position_is",
        "value": "Forward",
    },
    {
        "id": "position_center",
        "text": "Does the player primarily play Center?",
        "type": "position_is",
        "value": "Center",
    },
    {
        "id": "age_under_30",
        "text": "Is the player younger than 30?",
        "type": "age_lt",
        "value": 30,
    },
    {
        "id": "age_30_or_older",
        "text": "Is the player 30 or older?",
        "type": "age_gte",
        "value": 30,
    },
    {
        "id": "made_all_star",
        "text": "Has the player made an all-star team?",
        "type": "column_equals",
        "column": "made_all_star",
        "value": 1,
    },
    {
        "id": "won_championship",
        "text": "Has the player won a championship?",
        "type": "column_gte",
        "column": "num_championships",
        "value": 1,
    },
    {
        "id": "won_multiple_championships",
        "text": "Has the player won multiple championships?",
        "type": "column_gte",
        "column": "num_championships",
        "value": 2,
    },
    {
        "id": "won_mvp",
        "text": "Has the player won an MVP?",
        "type": "column_equals",
        "column": "won_mvp",
        "value": 1,
    },
    {
        "id": "won_dpoy",
        "text": "Has the player won a DPOY?",
        "type": "column_equals",
        "column": "won_dpoy",
        "value": 1,
    },
    {
        "id": "made_all_nba",
        "text": "Has the player made an All-NBA team?",
        "type": "column_equals",
        "column": "made_all_nba",
        "value": 1,
    },
    {
        "id": "made_all_defence",
        "text": "Has the player made an All-Defence team?",
        "type": "column_equals",
        "column": "made_all_defence",
        "value": 1,
    },
    {
        "id": "drafted_2020s",
        "text": "Was the player drafted in the 2020s?",
        "type": "draft_year_range",
        "min": 2020,
        "max": 2029,
        "requires_any_yes": [
            "drafted_first_round",
            "drafted_second_round",
        ],
    },
    {
        "id": "drafted_2010s",
        "text": "Was the player drafted in the 2010s?",
        "type": "draft_year_range",
        "min": 2010,
        "max": 2019,
        "requires_any_yes": [
            "drafted_first_round",
            "drafted_second_round",
        ],
    },
    {
        "id": "drafted_2000s",
        "text": "Was the player drafted in the 2000s?",
        "type": "draft_year_range",
        "min": 2000,
        "max": 2009,
        "requires_any_yes": [
            "drafted_first_round",
            "drafted_second_round",
        ],
    },
    {
        "id": "averaged_30_ppg",
        "text": "Has the player ever averaged 30 PPG for a season?",
        "type": "column_gte",
        "column": "ppg_career_high",
        "value": 30,
    },
    {
        "id": "averaged_15_ppg",
        "text": "Has the player ever averaged 15 PPG for a season?",
        "type": "column_gte",
        "column": "ppg_career_high",
        "value": 15,
    },
    {
        "id": "averaged_10_apg",
        "text": "Has the player ever averaged 10 APG for a season?",
        "type": "column_gte",
        "column": "apg_career_high",
        "value": 10,
    },
    {
        "id": "averaged_10_rpg",
        "text": "Has the player ever averaged 10 RPG for a season?",
        "type": "column_gte",
        "column": "rpg_career_high",
        "value": 10,
    },
    {
        "id": "played_in_playoffs",
        "text": "Has the player ever played in the Playoffs?",
        "type": "column_equals",
        "column": "played_in_playoffs",
        "value": 1,
    },
]


def build_team_questions(df):
    teams = sorted(df["team"].dropna().unique())

    return [
        {
            "id": f"team_{team.lower().replace(' ', '_')}",
            "text": f"Does the player play for the {team}?",
            "type": "team_is",
            "value": team,
        }
        for team in teams
    ]


def get_all_questions(df):
    return QUESTIONS + build_team_questions(df)