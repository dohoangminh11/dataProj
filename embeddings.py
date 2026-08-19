from dataanalysis import mbappe, messi, neymar, ronaldo, yamal
from indexing import build_or_update_index, semantic_search


documents = {
    8198: ronaldo,
    28003: messi,
    68290: neymar,
    342229: mbappe,
    937958: yamal,
}


if __name__ == "__main__":
    build_or_update_index(documents)

    for player_id, score in semantic_search(
        "best player at a young age in terms of market value",
        top_k=5,
    ):
        print(player_id, round(score, 4))
