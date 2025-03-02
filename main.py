# main.py
import sys
from extract import extract
from transform import transform
from load import load
import json

def display_menu():
    print("\n=== ProtonDB ETL Menu ===")
    print("1. Extract Data")
    print("2. Transform Data")
    print("3. Load Data (dan Visualisasi)")
    print("0. Keluar")
    choice = input("Pilih opsi (0-3): ")
    return choice

def main():
    games = None
    all_reports = None
    notes_data = None
    word_freq_data = None
    bigram_freq_data = None
    trigram_freq_data = None

    while True:
        choice = display_menu()

        if choice == "1":
            try:
                limit = int(input("Masukkan limit jumlah game (kosongkan untuk semua): ") or 0)
                games, all_reports = extract(limit if limit > 0 else None)
                print(f"Data berhasil diekstrak: {len(games)} game.")
            except ValueError as e:
                print(f"Input tidak valid: {e}")
            except Exception as e:
                print(f"Error saat ekstraksi: {e}")

        elif choice == "2":
            if games is None or all_reports is None:
                print("Mencoba memuat data ekstraksi dari file JSON sementara...")
                try:
                    with open("temp_games.json", 'r') as gf:
                        games = json.load(gf)
                    with open("temp_reports.json", 'r') as rf:
                        all_reports = json.load(rf)
                    print(f"Loaded {len(games)} games from temp files.")
                except FileNotFoundError:
                    print("File sementara tidak ditemukan. Silakan lakukan ekstraksi (opsi 1) terlebih dahulu!")
                    continue
            try:
                notes_data, word_freq_data, bigram_freq_data, trigram_freq_data = transform(games, all_reports)
                print(f"Transformasi selesai: {len(notes_data)} notes diproses.")
            except Exception as e:
                print(f"Error saat transformasi: {e}")

        elif choice == "3":
            if notes_data is None or word_freq_data is None or bigram_freq_data is None or trigram_freq_data is None:
                print("Mencoba memuat data transformasi dari file JSON sementara...")
                try:
                    with open("temp_notes.json", 'r') as nf:
                        notes_data = json.load(nf)
                    with open("temp_word_freq.json", 'r') as wf:
                        word_freq_data = json.load(wf)
                    with open("temp_bigram_freq.json", 'r') as bf:
                        bigram_freq_data = json.load(bf)
                    with open("temp_trigram_freq.json", 'r') as tf:
                        trigram_freq_data = json.load(tf)
                    print(f"Loaded {len(notes_data)} notes from temp files.")
                except FileNotFoundError:
                    print("File sementara tidak ditemukan. Silakan lakukan transformasi (opsi 2) terlebih dahulu!")
                    continue
            try:
                output_dir = load(notes_data, word_freq_data, bigram_freq_data, trigram_freq_data)
                print(f"Data berhasil disimpan di {output_dir}")
            except Exception as e:
                print(f"Error saat loading: {e}")

        elif choice == "0":
            print("Keluar dari program.")
            sys.exit(0)

        else:
            print("Opsi tidak valid, pilih antara 0-3.")

if __name__ == "__main__":
    main()
