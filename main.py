from pathlib import Path
import matplotlib.pyplot as plt

import kagglehub
import pandas as pd

def load_dataset_file(file:str) -> pd.DataFrame:
    dataset_path = Path(
        kagglehub.dataset_download("davidcariboo/player-scores")
    )
    return pd.read_csv(dataset_path / file)

def get_basic_info(data: pd.DataFrame) -> dict:
    return {
        "number_of_players": len(data),
        "number_of_columns": len(data.columns),
        "column_types": data.dtypes.astype(str).to_dict(),
    }

def format_euros(value: float | int) -> str:
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1_000_000_000:
        return f"€{value / 1_000_000_000:.2f}bn"
    return f"€{value / 1_000_000:.1f}m"

def format_euro_change(value: float | int) -> str:
    if pd.isna(value):
        return "N/A"

    return f"€{value / 1_000_000:+.1f}m"

def print_dataframe(data: pd.DataFrame, title: str | None = None) -> None:
    if title:
        print(f"\n{title}:")

    euro_columns = [
        column for column in data.columns
        if column.endswith("_in_eur")
    ]
    formatters = {
        
    column: (
        format_euro_change
        if column == "value_change_in_eur"
        else format_euros
    )
    for column in euro_columns
    }
    if "value_change_pct" in data.columns:
        formatters["value_change_pct"] = lambda value: (
            "N/A"
            if pd.isna(value)
            else f"{value:+.1f}%"
        )

    print(data.to_string(index=False, formatters=formatters))

def print_player_analytics(
    data: pd.DataFrame,
    title: str | None = None,
) -> None:
    if title:
        print(f"\n{title}:")

    display_data = data.copy()

    for column in display_data.columns:
        if column.endswith("_in_eur"):
            display_data[column] = display_data[column].map(
                format_euros
            )

        elif column.endswith("_pct"):
            display_data[column] = display_data[column].map(
                lambda value: (
                    "N/A"
                    if pd.isna(value)
                    else f"{value:+.1f}%"
                )
            )

        elif column.endswith("_date"):
            display_data[column] = pd.to_datetime(
                display_data[column],
                errors="coerce",
            ).dt.strftime("%Y-%m-%d")

    print(
        display_data.T
        .rename(columns={0: "value"})
        .to_string()
    )
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
        ["name", "market_value_in_eur", "current_club_name"]
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
    return under20.nlargest(count,"market_value_in_eur")[["name", "market_value_in_eur", "current_club_name"]]

def most_valuable_clubs(
    data: pd.DataFrame,
    count: int=10,
) -> pd.DataFrame:
    latest_season = data["last_season"].max()
    active_players = data[data["current_club_id"].notna() & data["last_season"].eq(latest_season)]
    club_values = active_players.groupby(
        "current_club_name")["market_value_in_eur"].sum()
    return club_values.nlargest(count).reset_index(name="total_market_value_in_eur")

def most_valuable_player_per_year(
    data: pd.DataFrame,
    count: int=10,
) -> pd.DataFrame:
    result = data.copy()
    result["date"] = pd.to_datetime(result["date"],errors="coerce",)  

    result = result.dropna(subset=["date", "market_value_in_eur"])
    result["year"] = result["date"].dt.year

    highest_value_rows = result.groupby("year")["market_value_in_eur"].idxmax()

    return (
        result.loc[
            highest_value_rows,
            ["year", "name", "market_value_in_eur"],
        ]
        .sort_values("year", ascending=False)
        .head(count)
    )
    
def show_player_evolution(
    data: pd.DataFrame,
    playerId : int,
) -> pd.DataFrame:
    evolution = data[data["player_id"].eq(playerId)].copy()
    evolution["date"] = pd.to_datetime(evolution["date"], errors="coerce")
    evolution = evolution.sort_values("date")

    evolution["value_change_in_eur"] = evolution["market_value_in_eur"].diff()
    evolution["value_change_pct"] = (
        evolution["market_value_in_eur"]
        .pct_change(fill_method=None)
        .mul(100)
        .round(2)
    )
    return evolution[["name", "market_value_in_eur", "date", "current_club_name", "value_change_in_eur", "value_change_pct"]]

def player_analytics(data: pd.DataFrame, playerId: int) -> pd.DataFrame:
    evolution = show_player_evolution(data,playerId).sort_values("date")
    if evolution.empty:
        return pd.DataFrame()
    
    first_rec_value = evolution.iloc[0]
    last_rec_value = evolution.iloc[-1]
    peak_value = evolution.loc[
        evolution["market_value_in_eur"].idxmax()
    ]
    min_value = evolution.loc[
        evolution["market_value_in_eur"].idxmin()
    ]
    recorded_changes = evolution.dropna(subset=["value_change_pct"])
    largest_valuation_increase = (
        recorded_changes.loc[recorded_changes["value_change_pct"].idxmax()]
        if not recorded_changes.empty
        else None
    )
    largest_valuation_decrease = (
        recorded_changes.loc[recorded_changes["value_change_pct"].idxmin()]
        if not recorded_changes.empty
        else None
    )

    return pd.DataFrame([{
        "player_name": evolution["name"].iloc[0],

        "first_recorded_value_in_eur":
            first_rec_value["market_value_in_eur"],
        "first_recorded_date":
            first_rec_value["date"],

        "last_recorded_value_in_eur":
            last_rec_value["market_value_in_eur"],
        "last_recorded_date":
            last_rec_value["date"],

        "peak_value_in_eur":
            peak_value["market_value_in_eur"],
        "peak_date":
            peak_value["date"],

        "minimum_value_in_eur":
            min_value["market_value_in_eur"],
        "minimum_date":
            min_value["date"],

        "largest_increase_pct":
            largest_valuation_increase["value_change_pct"]
            if largest_valuation_increase is not None else pd.NA,
        "largest_increase_date":
            largest_valuation_increase["date"]
            if largest_valuation_increase is not None else pd.NaT,

        "largest_decrease_pct":
            largest_valuation_decrease["value_change_pct"]
            if largest_valuation_decrease is not None else pd.NA,
        "largest_decrease_date":
            largest_valuation_decrease["date"]
            if largest_valuation_decrease is not None else pd.NaT,
    }])

# ================ Display ================

# ================ Main call ================
def main() -> None:
    players = load_dataset_file("players.csv")
    player_valuations = load_dataset_file("player_valuations.csv")
    df_player_valuation = pd.merge(
        players[["player_id", "name"]],
        player_valuations,
        on="player_id",
    )
    df_player_valuation["date"] = pd.to_datetime(df_player_valuation["date"],errors="coerce")
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

    print_dataframe(
        most_valuable_clubs(players, 10),
        "Most valuable clubs"
    )

    print_dataframe(
        most_valuable_player_per_year(
            df_player_valuation,
            count=20,
        ),
        "Most valuable player per year",
)
    print_dataframe(
        show_player_evolution(df_player_valuation,8198),
        "Cristiano Ronaldo's valuation throughout his career"
    ) 


    print_player_analytics(
        player_analytics(df_player_valuation, 8198),
        "Selected player's analytics"
        )
if __name__ == "__main__":
    main()
