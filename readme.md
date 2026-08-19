# Player Data Analysis

This project is my first attempt at loading, exploring, and manipulating a dataset with Python and pandas. Its purpose is to develop practical data-analysis skills and build a foundation for learning about machine learning and large language models (LLMs).

The project uses the [Player Scores](https://www.kaggle.com/datasets/davidcariboo/player-scores) dataset from Kaggle. The current analysis includes:

- inspecting the number of players and columns;
- identifying the data type of each column;
- sorting and filtering players by market value, nationality, age, and position;
- aggregating player and club valuations;
- examining individual player valuation histories; and
- calculating annual average valuations and year-over-year changes.

## Streamlit interface

The project includes a Streamlit dashboard for exploring individual player valuation histories. The interface provides:

- player lookup using a Transfermarkt player ID;
- a reference list of ten well-known player IDs;
- peak, first, and latest annual average market values;
- largest annual percentage rise and drop;
- a non-scrollable market-value evolution chart; and
- a static annual valuation table that can be ordered chronologically in ascending or descending order.

The table contains one row per year. When several valuations exist within a year, their mean is used as that year's market value.

### Authorship note

The data-analysis functions were handwritten as part of this pandas learning project. The Streamlit UI was designed and implemented with the assistance of AI agents, using the handwritten analysis as its foundation.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install pandas kagglehub matplotlib streamlit altair
```

## Run the project

```powershell
python main.py
```

To launch the Streamlit interface:

```powershell
python -m streamlit run page.py
```

Streamlit prints the local dashboard URL in the terminal, normally `http://localhost:8501`.

KaggleHub downloads the dataset when the program runs. Depending on the dataset's access requirements, Kaggle authentication may be necessary.

## Project status

This is a learning project rather than a finished analysis. The code and structure will evolve as I learn more about pandas, data cleaning, visualization, machine learning, and LLM-related workflows.
