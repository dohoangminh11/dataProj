from pathlib import Path

import kagglehub
import pandas as pd


def load_players() -> pd.DataFrame:
    dataset_path = Path(
        kagglehub.dataset_download("davidcariboo/player-scores")
    )
    return pd.read_csv(dataset_path / "players.csv")


def get_basic_info(data: pd.DataFrame) -> dict:
    return {
        "number_of_players": len(data),
        "number_of_columns": len(data.columns),
        "column_types": data.dtypes.astype(str).to_dict(),
    }


def format_euros(value: float | int) -> str:
    if pd.isna(value):
        return "N/A"
    return f"€{value / 1_000_000:.1f}m"


def print_dataframe(data: pd.DataFrame, title: str | None = None) -> None:
    if title:
        print(f"\n{title}:")

    euro_columns = [
        column for column in data.columns
        if column.endswith("_in_eur")
    ]
    formatters = {
        column: format_euros for column in euro_columns
    }

    print(data.to_string(index=False, formatters=formatters))

""" def add_age_col(data:pd.DataFrame) -> pd.DataFrame:
    data["date_of_birth"] = pd.to_datetime(data["date_of_birth"],errors="coerce")

    today = pd.Timestamp.today()
    
    data["age"] = (today.year - data["date_of_birth"].dt.year).astype("Int64")  """



# ================ Data sorting functions ================
def get_most_valuable_players(
    data: pd.DataFrame,
    count: int = 10,
) -> pd.DataFrame:
    return data.nlargest(count, "market_value_in_eur")[
        ["name", "market_value_in_eur"]
    ]

def get_centre_forwards(
    data: pd.DataFrame,
    count: int = 10,
) -> pd.DataFrame:
    centre_forwards = data[data["sub_position"].eq("Centre-Forward")]
    return get_most_valuable_players(
        centre_forwards,
        count=count)

def get_french_players_above20m(
    data: pd.DataFrame,
    count: int = 10,
) -> pd.DataFrame:
    french_players = data[data["country_of_citizenship"].eq("France")]
    above20m = french_players[french_players["market_value_in_eur"] > 20_000_000]
    return get_most_valuable_players(above20m, count)

def count_players_by_position(
    data: pd.DataFrame,
) -> pd.DataFrame:
    return (data["position"].value_counts().rename_axis("position").reset_index(name="player_count"))
    
def count_players_by_sub_position(
    data: pd.DataFrame,
) -> pd.DataFrame:
    return (data["sub_position"].value_counts().rename_axis("position").reset_index(name="player_count"))

def mean_median_value(
    data: pd.DataFrame,
) -> tuple[float, float]:
    return (data["market_value_in_eur"].mean(), data["market_value_in_eur"].median())

def sum_empty_cells(
    data:pd.DataFrame,
) -> pd.DataFrame:
    missing = data.isna().sum()
    missing = missing[missing>0]
    return (missing.rename_axis("column").reset_index(name="empty_cells"))

def most_valuable_teenagers(
    data: pd.DataFrame,
    count: int = 10,
) -> pd.DataFrame:
    df_age = data.copy()
    df_age["date_of_birth"] = pd.to_datetime(df_age["date_of_birth"],errors="coerce")
    today = pd.Timestamp.today()
    df_age["age"] = (today.year - df_age["date_of_birth"].dt.year).astype("Int64")
    under20 = df_age[df_age["age"] <= 21] #Cutoff date here is 20, but technically could be 21
    return under20.nlargest(count,"market_value_in_eur")[["name", "market_value_in_eur"]]



# ================ Main call ================
def main() -> None:
    players = load_players()
    printInfo = False
    info = get_basic_info(players)

    #Adding age column
    #add_age_col(players)

    top_players = get_most_valuable_players(players, count=10)

    if (printInfo):
        print("Dataset information:")
        print(info)

    print_dataframe(top_players, "Most valuable players")

    print_dataframe(
        get_centre_forwards(players, count=10),
        "Most valuable forwards",
    )

    print_dataframe(
        get_french_players_above20m(players, count=10),
        "Most valuable frenchies",
    )

    print_dataframe(
        count_players_by_position(players),
        "Players by position",
    )

    print("\nMean average value + median value (in euros):")
    mean_value, median_value = mean_median_value(players)
    print(format_euros(mean_value), format_euros(median_value))

    """ print("\nColumns with empty cells:")
    print(sum_empty_cells(players).to_string(index=False)) """
    #Interesting because this would affect median player value, wages, nb of players in a certain country etc... For later analysis.

    print_dataframe(
        most_valuable_teenagers(players, count=10),
        "Most valuable teenagers",
    )

if __name__ == "__main__":
    main()
