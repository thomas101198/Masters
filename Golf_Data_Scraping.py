import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time

# -----------------------------
# CONFIG
# -----------------------------
X_API_KEY = "da2-gsrx5bibzbb4njvhl7t37wqyl4"

YEAR = 20230
PAST_RESULTS_ID = "R2014014"

# -----------------------------
# STEP 1: GET PLAYER IDS (GRAPHQL)
# -----------------------------
payload = {
    "operationName": "TournamentPastResults",
    "variables": {
        "tournamentPastResultsId": PAST_RESULTS_ID,
        "year": YEAR
    },
    "query": """
    query TournamentPastResults($tournamentPastResultsId: ID!, $year: Int) {
      tournamentPastResults(id: $tournamentPastResultsId, year: $year) {
        players {
          player {
            id
          }
        }
      }
    }
    """
}

page = requests.post(
    "https://orchestrator.pgatour.com/graphql",
    json=payload,
    headers={"x-api-key": X_API_KEY}
)

page.raise_for_status()

data = page.json()["data"]["tournamentPastResults"]["players"]

player_ids = sorted({
    entry["player"]["id"]
    for entry in data
})

# -----------------------------
# SAVE BASE CSV (IDs ONLY)
# -----------------------------
players_df = pd.DataFrame({"player_id": player_ids})
players_df["player_id"] = players_df["player_id"].astype(str)

players_df.to_csv("players.csv", index=False)

print(f"Saved {len(players_df)} player IDs")

# -----------------------------
# STEP 2: BIO SCRAPER (NEXT.JS JSON)
# -----------------------------
def scrape_bio(player_id, session=None):
    url = f"https://www.pgatour.com/player/{player_id}"

    try:
        html = requests.get(url, timeout=15).text
        soup = BeautifulSoup(html, "html.parser")

        script = soup.find("script", {"id": "__NEXT_DATA__"})
        if not script:
            return {}

        data = json.loads(script.string)

        queries = data["props"]["pageProps"]["dehydratedState"]["queries"]

        bio_raw = None

        for q in queries:
            if q["queryKey"][0] == "playerProfileOverview":
                bio_raw = q["state"]["data"]["summaryData"]["summaryData"]
                break

        if not bio_raw:
            return {}

        return {
            "player_id": player_id,
            "first_name": bio_raw.get("firstName"),
            "last_name": bio_raw.get("lastName"),
            "country": bio_raw.get("country"),
            "age": bio_raw.get("age"),
            "born": bio_raw.get("born"),
            "turned_pro": bio_raw.get("turnedPro"),
            "college": bio_raw.get("college"),
            "birthplace": bio_raw.get("birthplace"),
        }

    except Exception as e:
        print(f"Error scraping {player_id}: {e}")
        return {}

# -----------------------------
# STEP 3: SCRAPE ALL BIOS
# -----------------------------
df = pd.read_csv("players.csv", dtype={"player_id": str})
player_ids = df["player_id"].astype(str).tolist()

rows = []

for i, pid in enumerate(player_ids):
    print(f"Scraping {i+1}/{len(player_ids)}: {pid}")

    bio = scrape_bio(pid)

    if bio:
        rows.append(bio)

    time.sleep(0.5)  # avoid hammering site

bio_df = pd.DataFrame(rows)

print(f"Scraped {len(bio_df)} bios")

# -----------------------------
# STEP 4: MERGE BACK INTO CSV
# -----------------------------
players_df = pd.read_csv("players.csv")

players_df["player_id"] = players_df["player_id"].astype(str)
bio_df["player_id"] = bio_df["player_id"].astype(str)

merged = players_df.merge(bio_df, on="player_id", how="left")

merged.to_csv("players.csv", index=False)

print("Updated players.csv with bio data")

# -----------------------------
# DONE
# -----------------------------