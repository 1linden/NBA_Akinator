"""
engine.py

Akinator engine for NBA players using rule-based questions.
The first question is randomized. After that, the engine chooses
questions that best split the remaining candidates.
If no remaining question can narrow the candidates further,
the engine makes a random guess from the remaining players.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import random

import pandas as pd

from questions import get_all_questions


@dataclass
class AkinatorEngine:
    players_df: pd.DataFrame
    candidates: pd.DataFrame = field(init=False)
    asked_question_ids: set[str] = field(default_factory=set, init=False)
    yes_answered_question_ids: set[str] = field(default_factory=set, init=False)
    questions: list[dict] = field(init=False)
    first_question_asked: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        required = {
            "player_name",
            "draft_pick_number",
            "draft_year",
            "position",
            "team",
            "age",
            "made_all_star",
            "num_championships",
            "won_mvp",
            "won_dpoy",
            "made_all_nba",
            "made_all_defence",
            "ppg_career_high",
            "apg_career_high",
            "rpg_career_high",
            "played_in_playoffs",
        }

        missing = required - set(self.players_df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        self.candidates = self.players_df.copy()
        self.questions = get_all_questions(self.players_df)

    def reset(self) -> None:
        self.candidates = self.players_df.copy()
        self.asked_question_ids.clear()
        self.yes_answered_question_ids.clear()
        self.first_question_asked = False

    def get_candidate_count(self) -> int:
        return len(self.candidates)

    def top_candidates(self, n: int = 5) -> list[str]:
        return self.candidates["player_name"].head(n).tolist()

    def question_is_unlocked(self, question: dict) -> bool:
        """
        Check whether dependency rules allow this question to be asked.
        """
        required_yes = question.get("requires_any_yes")
        if not required_yes:
            return True

        return any(qid in self.yes_answered_question_ids for qid in required_yes)

    def get_available_questions(self) -> list[dict]:
        return [
            q for q in self.questions
            if q["id"] not in self.asked_question_ids
            and self.question_is_unlocked(q)
        ]

    def question_matches_row(self, question: dict, row: pd.Series) -> bool:
        qtype = question["type"]

        if qtype == "draft_range":
            value = row["draft_pick_number"]
            return question["min"] <= value <= question["max"]

        if qtype == "draft_exact":
            return row["draft_pick_number"] == question["value"]

        if qtype == "draft_year_range":
            value = row["draft_year"]
            return question["min"] <= value <= question["max"]

        if qtype == "position_is":
            return str(row["position"]).strip().lower() == question["value"].lower()

        if qtype == "team_is":
            return str(row["team"]).strip().lower() == question["value"].lower()

        if qtype == "age_lt":
            return row["age"] < question["value"]

        if qtype == "age_gte":
            return row["age"] >= question["value"]

        if qtype == "column_equals":
            return row[question["column"]] == question["value"]

        if qtype == "column_gte":
            return row[question["column"]] >= question["value"]

        raise ValueError(f"Unsupported question type: {qtype}")

    def split_counts(self, question: dict) -> tuple[int, int]:
        yes_count = 0
        no_count = 0

        for _, row in self.candidates.iterrows():
            if self.question_matches_row(question, row):
                yes_count += 1
            else:
                no_count += 1

        return yes_count, no_count

    def has_useful_question(self) -> bool:
        """
        Return True if there exists at least one available question
        that actually splits the remaining candidates.
        """
        for q in self.get_available_questions():
            yes_count, no_count = self.split_counts(q)
            if yes_count > 0 and no_count > 0:
                return True
        return False

    def best_question(self) -> Optional[dict]:
        available = self.get_available_questions()

        if not available:
            return None

        useful_questions = []
        for q in available:
            yes_count, no_count = self.split_counts(q)
            if yes_count > 0 and no_count > 0:
                useful_questions.append((q, abs(yes_count - no_count)))

        if not useful_questions:
            return None

        if not self.first_question_asked:
            self.first_question_asked = True
            return random.choice([q for q, _ in useful_questions])

        best_q, _ = min(useful_questions, key=lambda item: item[1])
        return best_q

    def apply_answer(self, question: dict, answer: str) -> None:
        normalized = answer.strip().lower()

        if normalized not in {"yes", "no", "unknown"}:
            raise ValueError("Answer must be 'yes', 'no', or 'unknown'.")

        if normalized == "yes":
            mask = self.candidates.apply(
                lambda row: self.question_matches_row(question, row),
                axis=1,
            )
            self.candidates = self.candidates[mask]
            self.yes_answered_question_ids.add(question["id"])

        elif normalized == "no":
            mask = self.candidates.apply(
                lambda row: self.question_matches_row(question, row),
                axis=1,
            )
            self.candidates = self.candidates[~mask]

        elif normalized == "unknown":
            pass

        self.asked_question_ids.add(question["id"])

    def ready_to_guess(self) -> bool:
        if len(self.candidates) <= 1:
            return True

        # If no available question can narrow players further, guess now.
        return not self.has_useful_question()

    def guess_player(self) -> Optional[str]:
        if self.candidates.empty:
            return None

        random_index = random.randrange(len(self.candidates))
        return str(self.candidates.iloc[random_index]["player_name"])