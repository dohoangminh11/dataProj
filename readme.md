# Player Data Analysis

This project is my first attempt at loading, exploring, and manipulating a dataset with Python and pandas. Its purpose is to develop practical data-analysis skills and build a foundation for learning about machine learning and large language models (LLMs).

The project uses the [Player Scores](https://www.kaggle.com/datasets/davidcariboo/player-scores) dataset from Kaggle. The current analysis includes:

- inspecting the number of players and columns;
- identifying the data type of each column;
- sorting players by market value; and
- filtering players by position.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install pandas kagglehub
```

## Run the project

```powershell
python main.py
```

KaggleHub downloads the dataset when the program runs. Depending on the dataset's access requirements, Kaggle authentication may be necessary.

## Project status

This is a learning project rather than a finished analysis. The code and structure will evolve as I learn more about pandas, data cleaning, visualization, machine learning, and LLM-related workflows.
