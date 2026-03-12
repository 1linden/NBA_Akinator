# NBA Akinator 🏀
A Python desktop game inspired by Akinator that guesses which active NBA player you're thinking of by asking a series of questions about their career. The game uses real NBA data pulled from the nba_api to generate player attributes and intelligently narrow down possible players.

## Demo
### Start Screen
![Start Screen](images/start_screen.PNG)
### Question Screen
![Question Screen](images/question_screen.PNG)
### Guess Screen
![Guess Screen](images/guess_screen.PNG)

## Features
- 🧠 **Intelligent question selection**  
  The engine selects questions that best split the remaining players.
- 📊 **Real NBA data**  
  Player information is collected using the nba_api.
- 🎨 **Dynamic UI reactions**
  - Neutral background normally
  - Happy background after multiple Yes answers
  - Mad background after multiple No answers
- 🔢 **Question counter**  
  Tracks how many questions the engine used before guessing.
- 🎯 **Fallback guessing**  
  If no remaining questions can narrow players further, the engine makes a random guess from the remaining candidates.

## Example Questions
The engine may ask questions like:
- Was the player drafted in the first round?
- Does the player primarily play Guard?
- Has the player made an All-Star team?
- Has the player ever averaged 30 PPG for a season?
- Has the player ever played in the Playoffs?

These questions progressively narrow down the player pool.

## Dataset

The game builds a dataset of **active NBA players** with attributes such as:

| Column | Description |
|------|-------------|
| player_name | Player's full name |
| team | Player's current NBA team |
| age | Player's age |
| draft_year | Player's draft year |
| draft_pick_number | Player's draft pick Number (61 = undrafted) |
| position | Player's Primary position (G / F / C) |
| made_all_star | Whether player has made an All-Star team 
| made_all_nba | Whether player has made an All-NBA team |
| made_all_defence | Whether player has made an All-Defense team |
| won_dpoy | Whether player has won Defensive Player of the Year |
| won_mvp | Whether player has won Most Valuable Player |
| played_in_playoffs | Whether player has appeared in the playoffs |
| num_championships | Number of championships won by Player |
| ppg_career_high | Player's highest points per game (season) |
| apg_career_high | Player's highest assists per game (season) |
| rpg_career_high | Player's highest rebounds per game (season) |

The dataset is generated using:

- `CommonPlayerInfo`
- `PlayerAwards`
- `PlayerCareerStats`

from the nba_api.

## Project Structure:
- `app.py`
- `build_dataset.py`
- `engine.py`
- `questions.py`
- `UI_Background/`
    - `background_happy.png`
    - `background_mad.png`
    - `background_neutral.png`
- `images/`
    - `guess_screen.PNG`
    - `question_screen.PNG`
    - `start_screen.PNG`
- `active_nba_players.csv` 

## Installation and Execution
### 1. Clone the Repository
```
git clone https://github.com/1linden/NBA_Akinator.git
```
### 2. Install Dependencies
```
pip install -r requirements.txt
```
### 3. Build the Player Dataset
```
python build_dataset.py 1
python build_dataset.py 2
python build_dataset.py 3
python build_dataset.py 4
```
### 4. Run the Game
```
python app.py
```

## How the Guessing Engine Works

1. Start with all players as candidates.
2. Ask questions that best split the remaining players.
3. Remove players who are inconsistent with the user's answers.
4. Repeat the process until:
   - Only one player remains, or
   - No remaining question can further split the remaining players, so the engine makes a random guess from the remaining players.

## Technologies Used
- Python  
- tkinter – desktop GUI  
- pandas – dataset processing  
- nba_api – player data

## License
This project is for educational purposes and is not affiliated with the NBA.
