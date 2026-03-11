import os
import tkinter as tk
from tkinter import messagebox

import pandas as pd

from engine import AkinatorEngine


CSV_FILE = "active_nba_players.csv"

BACKGROUND_NEUTRAL = "UI_Background/background_neutral.png"
BACKGROUND_HAPPY = "UI_Background/background_happy.png"
BACKGROUND_MAD = "UI_Background/background_mad.png"


class NBAAkinatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("NBA Akinator")
        self.root.geometry("1100x600")
        self.root.resizable(False, False)

        self.bg_image = None
        self.current_question = None
        self.current_background = BACKGROUND_NEUTRAL

        self.yes_streak = 0
        self.no_streak = 0
        self.questions_asked_count = 0

        try:
            self.players_df = pd.read_csv(CSV_FILE)
        except Exception as exc:
            messagebox.showerror("CSV Error", f"Could not load {CSV_FILE}\n\n{exc}")
            self.root.destroy()
            return

        try:
            self.engine = AkinatorEngine(self.players_df)
        except Exception as exc:
            messagebox.showerror("Engine Errors", str(exc))
            self.root.destroy()
            return

        self.canvas = tk.Canvas(self.root, width=900, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.show_start_screen()

    def setup_background(self) -> None:
        """
        Draw the current background image if available,
        otherwise use a dark fallback.
        """
        if os.path.exists(self.current_background):
            try:
                self.bg_image = tk.PhotoImage(file=self.current_background)
                self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            except tk.TclError:
                self.canvas.create_rectangle(0, 0, 1100, 600, fill="#111111", outline="")
        else:
            self.canvas.create_rectangle(0, 0, 1100, 600, fill="#111111", outline="")

        #self.canvas.create_rectangle(0, 0, 1100, 600, fill="black", stipple="gray50", outline="")

    def clear_screen(self) -> None:
        self.canvas.delete("all")
        self.setup_background()

    def set_background(self, background_file: str) -> None:
        """
        Update the current background and redraw the current screen.
        """
        self.current_background = background_file

    def update_background_from_streaks(self) -> None:
        """
        Rules:
        - 3 no answers in a row -> mad
        - 2 yes answers in a row -> happy
        - otherwise -> neutral
        """
        if self.no_streak >= 3:
            self.set_background(BACKGROUND_MAD)
        elif self.yes_streak >= 2:
            self.set_background(BACKGROUND_HAPPY)
        else:
            self.set_background(BACKGROUND_NEUTRAL)

    def show_start_screen(self) -> None:
        self.set_background(BACKGROUND_NEUTRAL)
        self.clear_screen()

        title = tk.Label(
            self.root,
            text="NBA Akinator",
            font=("Georgia", 34, "bold"),
            fg="white",
            bg="#111111"
        )

        subtitle = tk.Label(
            self.root,
            text="Think of an NBA player",
            font=("Georgia", 18),
            fg="white",
            bg="#111111"
        )

        start_button = tk.Button(
            self.root,
            text="Start Game",
            font=("Georgia", 18, "bold"),
            width=14,
            command=self.start_game
        )

        self.canvas.create_window(450, 180, window=title)
        self.canvas.create_window(450, 250, window=subtitle)
        self.canvas.create_window(450, 360, window=start_button)

    def start_game(self) -> None:
        self.engine.reset()
        self.current_question = None
        self.yes_streak = 0
        self.no_streak = 0
        self.questions_asked_count = 0
        self.set_background(BACKGROUND_NEUTRAL)
        self.build_game_screen()
        self.update_question()

    def build_game_screen(self) -> None:
        self.clear_screen()

        self.question_label = tk.Label(
            self.root,
            text="",
            font=("Georgia", 20, "bold"),
            fg="white",
            bg="#111111",
            wraplength=700,
            justify="center"
        )

        self.remaining_label = tk.Label(
            self.root,
            text="",
            font=("Georgia", 12),
            fg="white",
            bg="#111111"
        )

        self.candidates_label = tk.Label(
            self.root,
            text="",
            font=("Georgia", 11),
            fg="#dddddd",
            bg="#111111",
            wraplength=700,
            justify="center"
        )

        self.questions_asked_label = tk.Label(
            self.root,
            text="",
            font=("Georgia", 20, "bold"),
            fg="white",
            bg="#111111"
        )
        
        self.yes_button = tk.Button(
            self.root,
            text="Yes",
            font=("Georgia", 14, "bold"),
            width=12,
            command=lambda: self.answer("yes")
        )

        self.no_button = tk.Button(
            self.root,
            text="No",
            font=("Georgia", 14, "bold"),
            width=12,
            command=lambda: self.answer("no")
        )

        self.unknown_button = tk.Button(
            self.root,
            text="Don't Know",
            font=("Georgia", 14, "bold"),
            width=12,
            command=lambda: self.answer("unknown")
        )

        self.restart_button = tk.Button(
            self.root,
            text="Restart",
            font=("Georgia", 12, "bold"),
            width=12,
            command=self.show_start_screen
        )

        self.canvas.create_window(450, 180, window=self.question_label)
        self.canvas.create_window(920, 550, window=self.questions_asked_label)
        '''
        self.canvas.create_window(450, 280, window=self.remaining_label)
        self.canvas.create_window(450, 330, window=self.candidates_label)
        '''
        self.canvas.create_window(280, 430, window=self.yes_button)
        self.canvas.create_window(450, 430, window=self.no_button)
        self.canvas.create_window(620, 430, window=self.unknown_button)

        self.canvas.create_window(450, 520, window=self.restart_button)

    def redraw_game_screen(self) -> None:
        """
        Rebuild the game screen after a background change,
        then restore the current text.
        """
        question_text = self.question_label.cget("text")
        remaining_text = self.remaining_label.cget("text")
        candidates_text = self.candidates_label.cget("text")
        questions_asked_text = self.questions_asked_label.cget("text")

        yes_state = self.yes_button.cget("state")
        no_state = self.no_button.cget("state")
        unknown_state = self.unknown_button.cget("state")

        self.build_game_screen()

        self.question_label.config(text=question_text)
        self.remaining_label.config(text=remaining_text)
        self.candidates_label.config(text=candidates_text)
        self.questions_asked_label.config(text=questions_asked_text)

        self.yes_button.config(state=yes_state)
        self.no_button.config(state=no_state)
        self.unknown_button.config(state=unknown_state)

    def update_question(self) -> None:
        if not self.engine.ready_to_guess():
            self.current_question = self.engine.best_question()

            if self.current_question is None:
                self.show_guess()
                return

            self.question_label.config(text=self.current_question["text"])
            self.questions_asked_label.config(
                text=f"Questions asked: {self.questions_asked_count}"
            )
            
            self.remaining_label.config(
                text=f"Remaining players: {self.engine.get_candidate_count()}"
            )

            top_names = self.engine.top_candidates(5)
            self.candidates_label.config(
                text="Top remaining: " + ", ".join(top_names)
            )
            
            self.yes_button.config(state="normal")
            self.no_button.config(state="normal")
            self.unknown_button.config(state="normal")
        else:
            self.show_guess()

    def answer(self, response: str) -> None:
        if self.current_question is None:
            return

        try:
            self.engine.apply_answer(self.current_question, response)
            self.questions_asked_count += 1

            if response == "yes":
                self.yes_streak += 1
                self.no_streak = 0
            elif response == "no":
                self.no_streak += 1
                self.yes_streak = 0
            else:
                self.yes_streak = 0
                self.no_streak = 0

            self.update_background_from_streaks()
            self.redraw_game_screen()
            self.update_question()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def show_guess(self) -> None:
        guess = self.engine.guess_player()

        self.set_background(BACKGROUND_HAPPY)
        self.redraw_game_screen()

        self.yes_button.config(state="disabled")
        self.no_button.config(state="disabled")
        self.unknown_button.config(state="disabled")

        self.questions_asked_label.config(
            text=f"Questions asked: {self.questions_asked_count}"
        )

        if guess is None:
            self.question_label.config(text="I couldn't guess the player.")
            self.remaining_label.config(text="No matching player remained.")
            self.candidates_label.config(text="")
        else:
            self.question_label.config(text=f"My guess is: {guess}")
            self.remaining_label.config(
                text=f"Final candidate count: {self.engine.get_candidate_count()}"
            )
            self.candidates_label.config(text="")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    root = tk.Tk()
    app = NBAAkinatorApp(root)
    app.run()


if __name__ == "__main__":
    main()