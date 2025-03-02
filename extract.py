# extract.py
import requests
import json
import os

def extract_games():
    url = "https://protondb.max-p.me/games/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch games. Status code: {response.status_code}")

def extract_reports(app_id):
    url = f"https://protondb.max-p.me/games/{app_id}/reports/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch reports for appId {app_id}. Status code: {response.status_code}")
        return []

def extract(limit=None):
    print("Starting extraction process...")
    games_file = "temp_games.json"
    reports_file = "temp_reports.json"

    # Cek apakah data sudah ada dalam file sementara
    if os.path.exists(games_file) and os.path.exists(reports_file):
        print("Loading existing extracted data from JSON files...")
        with open(games_file, 'r') as gf:
            games = json.load(gf)
        with open(reports_file, 'r') as rf:
            all_reports = json.load(rf)
        print(f"Loaded {len(games)} games from {games_file}")
        return games, all_reports

    # Jika tidak ada, lakukan ekstraksi
    games = extract_games()
    if limit:
        games = games[:limit]
        print(f"Limiting to {limit} games...")
    else:
        print(f"Processing all {len(games)} games...")

    all_reports = {}
    for game in games:
        app_id = game["appId"]
        print(f"Extracting reports for {game['title']} (appId: {app_id})...")
        all_reports[app_id] = extract_reports(app_id)

    # Simpan ke file JSON sementara
    with open(games_file, 'w') as gf:
        json.dump(games, gf)
    with open(reports_file, 'w') as rf:
        json.dump(all_reports, rf)
    print(f"Extracted data saved to {games_file} and {reports_file}")
    print("Extraction completed!")
    return games, all_reports
