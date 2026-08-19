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
    above20m = french_players[french_players["market_value_in_eur"] > 20000000]
    return get_most_valuable_players(above20m, count)



# ================ Main call ================
def main() -> None:
    players = load_players()
    printInfo = False
    info = get_basic_info(players)
    top_players = get_most_valuable_players(players, count=10)

    if (printInfo):
        print("Dataset information:")
        print(info)

    print("\nMost valuable players:")
    print(top_players.to_string(index=False))

    print("\nMost valuable forwards:")
    print(get_centre_forwards(players, count=10).to_string(index=False))

    print("\nMost valuable frenchies:")
    print(get_french_players_above20m(players, count=10).to_string(index=False))

if __name__ == "__main__":
    main()