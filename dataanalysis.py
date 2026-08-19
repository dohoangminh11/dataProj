import pandas as pd
import json
from main import load_dataset_file
from typing import TypedDict

players = load_dataset_file("players.csv")
valuations = load_dataset_file("player_valuations.csv")
df_player_valuation = pd.merge(
    players[["player_id", "name"]],
    valuations,
    on="player_id",
)
df_player_valuation["date"] = pd.to_datetime(df_player_valuation["date"],errors="coerce")

print("DB check: (false -> good)",players.empty, valuations.empty)

class PlayerDocument(TypedDict):
    player_id: int
    name: str
    position: str
    career_summary: dict[str, int]
    yearly_valuations: list[dict[str, int | float | None]]

def build_player_document(
    data: pd.DataFrame,
    playerId: int,
) -> PlayerDocument:
    player_rows = players.loc[players["player_id"].eq(playerId)]
    if player_rows.empty:
        raise ValueError(f"Player ID {playerId} was not found.")

    player = player_rows.iloc[0]
    evolution = data.loc[data["player_id"].eq(playerId)].copy()
    if evolution.empty:
        raise ValueError(f"No valuations found for player ID {playerId}.")

    evolution["date"] = pd.to_datetime(evolution["date"], errors="coerce")
    evolution = evolution.dropna(subset=["date", "market_value_in_eur"])
    evolution["year"] = evolution["date"].dt.year

    # One compact record per year instead of one record per valuation change.
    yearly = (
        evolution.groupby("year", as_index=False)["market_value_in_eur"]
        .mean()
        .rename(columns={"market_value_in_eur": "average_value_eur"})
        .sort_values("year")
    )
    yearly["average_value_eur"] = yearly["average_value_eur"].round().astype(int)
    yearly["change_pct"] = (
        yearly["average_value_eur"]
        .pct_change(fill_method=None)
        .mul(100)
        .round(1)
    )

    peak = yearly.loc[yearly["average_value_eur"].idxmax()]
    yearly_records = [
        {
            "year": int(row.year),
            "average_value_eur": int(row.average_value_eur),
            "change_pct": None if pd.isna(row.change_pct) else float(row.change_pct),
        }
        for row in yearly.itertuples(index=False)
    ]

    return {
        "player_id": playerId,
        "name": player["name"],
        "position": player["position"],
        "career_summary": {
            "first_year": int(yearly.iloc[0]["year"]),
            "latest_year": int(yearly.iloc[-1]["year"]),
            "peak_year": int(peak["year"]),
            "peak_average_value_eur": int(peak["average_value_eur"]),
        },
        "yearly_valuations": yearly_records,
    }

def player_document_to_text(document: PlayerDocument) -> str:
    """Convert a player document into compact text suitable for embedding."""
    history = document["yearly_valuations"]
    if not history:
        return (
            f'{document["name"]} is a football player whose position is '
            f'{document["position"]}. No market valuation history is available.'
        )

    first = history[0]
    latest = history[-1]
    first_value = int(first["average_value_eur"])
    latest_value = int(latest["average_value_eur"])
    summary = document["career_summary"]

    if first_value:
        overall_change_pct = ((latest_value - first_value) / first_value) * 100
        direction = "increased" if overall_change_pct >= 0 else "decreased"
        overall_trend = (
            f"The annual average valuation {direction} by "
            f"{abs(overall_change_pct):.1f}% across this period."
        )
    else:
        overall_trend = "The overall percentage change is unavailable."

    yearly_history = "; ".join(
        f'{int(record["year"])}: EUR {int(record["average_value_eur"]):,}'
        for record in history
    )

    return " ".join(
        [
            f'{document["name"]} is a football player whose position is '
            f'{document["position"]}.',
            f'Market valuation data covers {summary["first_year"]} to '
            f'{summary["latest_year"]}.',
            f'The peak annual average market value was EUR '
            f'{summary["peak_average_value_eur"]:,} in {summary["peak_year"]}.',
            f'The latest annual average market value was EUR '
            f'{latest_value:,} in {int(latest["year"])}.',
            overall_trend,
            f"Annual average market values by year: {yearly_history}.",
        ]
    )


def player_document_to_json(document: PlayerDocument) -> str:
    return json.dumps(
        document,
        ensure_ascii=False,
        separators=(",", ":"),
    )

ronaldo = player_document_to_text(build_player_document(df_player_valuation,8198))
messi = player_document_to_text(build_player_document(df_player_valuation,28003))
mbappe = player_document_to_text(build_player_document(df_player_valuation,342229))
neymar = player_document_to_text(build_player_document(df_player_valuation,68290))
yamal = player_document_to_text(build_player_document(df_player_valuation,937958))
