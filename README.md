# NBA Akinator 🏀
A Python desktop game inspired by Akinator that guesses which NBA player you are thinking of by asking a series of questions about their career. The game uses real NBA data pulled from the NBA Stats API to generate player attributes and intelligently narrow down possible players.

---

## Demo
### Start Screen
![Start Screen](images/start_screen.PNG)
### Question Screen
![Question Screen](images/question_screen.PNG)
### Guess Screen
![Guess Screen](images/guess_screen.PNG)

---

## Environment setup
```
pip install -r requirements.txt
```

## Repo structure:
- `app.py`
- `collect_data.py`
- `engine.py`
- `questions.py`
- `UI_Background/`
    - `background_happy.png`
    - `background_mad.png`
    - `background_neutral.png`
- `active_nba_players.csv`

## Execution
```
python app.py
```

## Technologies Used
Technologies Used
Python
Tkinter – desktop GUI
Pandas – dataset processing
NBA Stats API – player data
