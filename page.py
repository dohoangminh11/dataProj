import altair as alt
import pandas as pd
import streamlit as st

from main import load_dataset_file, show_player_evolution


st.set_page_config(
    page_title="Football Data Explorer",
    page_icon="\u26bd",
    layout="centered",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 900px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading football data...")
def load_data() -> pd.DataFrame:
    players = load_dataset_file("players.csv")
    valuations = load_dataset_file("player_valuations.csv")

    player_details = players[
        ["player_id", "name"]
    ].drop_duplicates("player_id")

    return valuations.merge(
        player_details,
        on="player_id",
        how="inner",
    )


def format_value(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1_000_000_000:
        return f"\u20ac{value / 1_000_000_000:.2f}bn"
    return f"\u20ac{value / 1_000_000:.1f}m"


def format_percentage(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:+.1f}%"


def yearly_player_evolution(evolution: pd.DataFrame) -> pd.DataFrame:
    yearly_source = evolution.dropna(
        subset=["date", "market_value_in_eur"]
    ).copy()
    yearly_source["year"] = yearly_source["date"].dt.year

    yearly = (
        yearly_source
        .groupby("year", as_index=False)
        .agg(
            market_value_in_eur=("market_value_in_eur", "mean"),
            current_club_name=(
                "current_club_name",
                lambda clubs: " / ".join(
                    dict.fromkeys(clubs.dropna().astype(str))
                ),
            ),
        )
        .sort_values("year")
    )
    yearly["value_change_pct"] = (
        yearly["market_value_in_eur"]
        .pct_change(fill_method=None)
        .mul(100)
    )

    return yearly


valuations = load_data()

available_player_ids = set(valuations["player_id"].dropna().astype(int))

popular_players = [
    ("Cristiano Ronaldo", 8198),
    ("Lionel Messi", 28003),
    ("Neymar", 68290),
    ("Kylian Mbappé", 342229),
    ("Erling Haaland", 418560),
    ("Luka Modrić", 27992),
    ("Mohamed Salah", 148455),
    ("Kevin De Bruyne", 88755),
    ("Robert Lewandowski", 38253),
    ("Vinicius Junior", 371998),
]

if "selected_player_id" not in st.session_state:
    st.session_state.selected_player_id = 8198

st.title("Football Data Explorer")
st.caption("Explore a player's recorded market-value history.")

with st.form("player_search"):
    entered_player_id = st.number_input(
        "Player ID",
        min_value=0,
        value=st.session_state.selected_player_id,
        step=1,
        help="Enter a Transfermarkt player ID from this dataset.",
    )
    search_submitted = st.form_submit_button("Search")

if search_submitted:
    entered_player_id = int(entered_player_id)
    if entered_player_id in available_player_ids:
        st.session_state.selected_player_id = entered_player_id
    else:
        st.error(f"Player ID {entered_player_id} was not found in this dataset.")

popular_player_note = "  ·  ".join(
    f"{name} (`{player_id}`)" for name, player_id in popular_players
)
st.info(f"Popular player IDs: {popular_player_note}")

selected_player_id = st.session_state.selected_player_id
selected_player = valuations[
    valuations["player_id"].eq(selected_player_id)
].iloc[0]
st.caption(
    f"Showing **{selected_player['name']}** "
    f"· Player ID `{selected_player_id}`"
)

evolution = show_player_evolution(valuations, selected_player_id)
yearly_evolution = yearly_player_evolution(evolution)

if yearly_evolution.empty:
    st.warning("No valuation history is available for this player.")
    st.stop()

first_year = yearly_evolution.iloc[0]
latest_year = yearly_evolution.iloc[-1]
peak_year = yearly_evolution.loc[
    yearly_evolution["market_value_in_eur"].idxmax()
]
annual_changes = yearly_evolution.dropna(subset=["value_change_pct"])
largest_rise = (
    annual_changes["value_change_pct"].max()
    if not annual_changes.empty else pd.NA
)
largest_drop = (
    annual_changes["value_change_pct"].min()
    if not annual_changes.empty else pd.NA
)

peak_col, first_col, latest_col = st.columns(3)
peak_col.metric(
    "Peak Value",
    format_value(peak_year["market_value_in_eur"]),
    border=True,
)
first_col.metric(
    "First Value",
    format_value(first_year["market_value_in_eur"]),
    border=True,
)
latest_col.metric(
    "Latest",
    format_value(latest_year["market_value_in_eur"]),
    border=True,
)

rise_col, drop_col, spacer_col = st.columns(3)
rise_col.metric(
    "Largest Rise",
    format_percentage(largest_rise),
    border=True,
)
drop_col.metric(
    "Largest Drop",
    format_percentage(largest_drop),
    border=True,
)
spacer_col.empty()

st.subheader("Market value evolution")

chart_data = yearly_evolution[["year", "market_value_in_eur"]].copy()
chart_data["Market value (\u20acm)"] = chart_data["market_value_in_eur"] / 1_000_000

value_chart = (
    alt.Chart(chart_data)
    .mark_line(point=True)
    .encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("Market value (\u20acm):Q", title="Market value (\u20acm)"),
        tooltip=[
            alt.Tooltip("year:O", title="Year"),
            alt.Tooltip(
                "Market value (\u20acm):Q",
                title="Market value (\u20acm)",
                format=".1f",
            ),
        ],
    )
    .properties(height=360)
)

st.altair_chart(value_chart, width="stretch")

with st.expander("View annual valuation records"):
    sort_order = st.radio(
        "Year order",
        options=["Ascending", "Descending"],
        horizontal=True,
        label_visibility="collapsed",
    )

    records = yearly_evolution[
        [
            "current_club_name",
            "year",
            "market_value_in_eur",
            "value_change_pct",
        ]
    ].copy()
    records = records.sort_values(
        "year",
        ascending=sort_order == "Ascending",
    )
    records["market_value_in_eur"] = records["market_value_in_eur"].map(
        format_value
    )
    records["value_change_pct"] = records["value_change_pct"].map(
        format_percentage
    )
    records["current_club_name"] = (
        records["current_club_name"]
        .replace("", "Unknown club")
        .fillna("Unknown club")
    )
    records = records.rename(
        columns={
            "current_club_name": "Club",
            "year": "Year",
            "market_value_in_eur": "Market value",
            "value_change_pct": "Annual change",
        }
    )

    st.table(records.set_index("Club"))
