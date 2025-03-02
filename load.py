# load.py
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from wordcloud import WordCloud
import json
import numpy as np
from collections import Counter

def load(notes_data, word_freq_data, bigram_freq_data, trigram_freq_data):
    print("Starting loading process...")

    # Simpan data sementara ke JSON
    temp_notes_file = "temp_notes.json"
    temp_word_freq_file = "temp_word_freq.json"
    temp_bigram_freq_file = "temp_bigram_freq.json"
    temp_trigram_freq_file = "temp_trigram_freq.json"

    with open(temp_notes_file, 'w') as nf:
        json.dump(notes_data, nf)
    with open(temp_word_freq_file, 'w') as wf:
        json.dump(word_freq_data, wf)
    with open(temp_bigram_freq_file, 'w') as bf:
        json.dump(bigram_freq_data, bf)
    with open(temp_trigram_freq_file, 'w') as tf:
        json.dump(trigram_freq_data, tf)
    print(f"Temporary data saved to {temp_notes_file}, {temp_word_freq_file}, {temp_bigram_freq_file}, {temp_trigram_freq_file}")

    # Lanjutkan dengan penyimpanan permanen dan visualisasi
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    notes_csv = f"{output_dir}/protondb_notes_{timestamp}.csv"
    word_freq_csv = f"{output_dir}/protondb_word_freq_{timestamp}.csv"
    bigram_freq_csv = f"{output_dir}/protondb_bigram_freq_{timestamp}.csv"
    trigram_freq_csv = f"{output_dir}/protondb_trigram_freq_{timestamp}.csv"
    notes_db = f"{output_dir}/protondb_notes_analysis_{timestamp}.db"

    notes_df = pd.DataFrame(notes_data)
    word_freq_df = pd.DataFrame(word_freq_data)
    bigram_freq_df = pd.DataFrame(bigram_freq_data)
    trigram_freq_df = pd.DataFrame(trigram_freq_data)

    notes_df.to_csv(notes_csv, index=False)
    word_freq_df.to_csv(word_freq_csv, index=False)
    bigram_freq_df.to_csv(bigram_freq_csv, index=False)
    trigram_freq_df.to_csv(trigram_freq_csv, index=False)
    print(f"Notes saved to {notes_csv}")
    print(f"Word frequency saved to {word_freq_csv}")
    print(f"Bigram frequency saved to {bigram_freq_csv}")
    print(f"Trigram frequency saved to {trigram_freq_csv}")

    conn = sqlite3.connect(notes_db)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            note_text TEXT,
            word_count INTEGER,
            char_count INTEGER,
            sentence_count INTEGER,
            avg_word_length REAL,
            lexical_diversity REAL,
            tokens TEXT,
            stemmed_tokens TEXT,
            lemmatized_tokens TEXT,
            noun_count INTEGER,
            verb_count INTEGER,
            adjective_count INTEGER,
            adverb_count INTEGER,
            entities TEXT,
            sentiment TEXT,
            compound_score REAL,
            positive_score REAL,
            negative_score REAL,
            neutral_score REAL,
            topic_category TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS word_freq (
            word TEXT,
            frequency INTEGER
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bigram_freq (
            bigram TEXT,
            frequency INTEGER
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS trigram_freq (
            trigram TEXT,
            frequency INTEGER
        )
    ''')
    notes_df.to_sql("notes", conn, if_exists="replace", index=False)
    word_freq_df.to_sql("word_freq", conn, if_exists="replace", index=False)
    bigram_freq_df.to_sql("bigram_freq", conn, if_exists="replace", index=False)
    trigram_freq_df.to_sql("trigram_freq", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print(f"Notes analysis saved to {notes_db}")

    print("\n=== DETAILED ANALYSIS RESULTS ===\n")

    # 1. Issue Categories Analysis
    topic_counts = notes_df["topic_category"].value_counts()
    print("1. DISTRIBUTION OF ISSUE CATEGORIES:")
    print("-" * 50)
    for category, count in topic_counts.items():
        percentage = (count / len(notes_df)) * 100
        print(f"- {category}: {count} reports ({percentage:.1f}%)")
    print()

    # 2. Sentiment Analysis
    sentiment_counts = notes_df["sentiment"].value_counts()
    print("2. USER SENTIMENT ANALYSIS:")
    print("-" * 50)
    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(notes_df)) * 100
        print(f"- {sentiment.title()}: {count} reports ({percentage:.1f}%)")
    
    # Calculate average sentiment scores
    avg_compound = notes_df["compound_score"].mean()
    print(f"\nOverall Sentiment Score: {avg_compound:.3f}")
    print(f"(Positive > 0.05, Neutral: -0.05 to 0.05, Negative < -0.05)\n")

    # 3. Performance Terms Analysis
    print("3. PERFORMANCE-RELATED TERMS FREQUENCY:")
    print("-" * 50)
    performance_words = ["fps", "performance", "smooth", "lag", "stutter", "slow", "fast", "run"]
    perf_freq = {w["word"]: w["frequency"] for w in word_freq_data if w["word"] in performance_words}
    for word, freq in sorted(perf_freq.items(), key=lambda x: x[1], reverse=True):
        print(f"- '{word}' mentioned {freq} times")
    print()

    # 4. Parts of Speech Analysis by Sentiment
    print("4. LANGUAGE USAGE BY SENTIMENT:")
    print("-" * 50)
    pos_by_sentiment = notes_df.groupby("sentiment")[["noun_count", "verb_count", "adjective_count", "adverb_count"]].mean()
    for sentiment in pos_by_sentiment.index:
        print(f"\n{sentiment.title()} Reviews Average Word Usage:")
        for pos in ["noun_count", "verb_count", "adjective_count", "adverb_count"]:
            print(f"- {pos.replace('_count', 's').title()}: {pos_by_sentiment.loc[sentiment, pos]:.1f}")
    print()

    # 5. Most Common Words by Sentiment
    print("5. MOST COMMON WORDS BY SENTIMENT:")
    print("-" * 50)
    for sentiment in ["positive", "negative", "neutral"]:
        sentiment_tokens = " ".join(notes_df[notes_df["sentiment"] == sentiment]["tokens"]).split()
        word_freq = Counter(sentiment_tokens).most_common(5)
        print(f"\n{sentiment.title()} Review Common Words:")
        for word, count in word_freq:
            print(f"- '{word}': {count} times")
    print()

    # 6. Review Length Analysis
    print("6. REVIEW LENGTH STATISTICS BY CATEGORY:")
    print("-" * 50)
    length_stats = notes_df.groupby("topic_category")["word_count"].agg(['mean', 'min', 'max'])
    for category in length_stats.index:
        stats = length_stats.loc[category]
        print(f"\n{category}:")
        print(f"- Average length: {stats['mean']:.1f} words")
        print(f"- Range: {stats['min']} to {stats['max']} words")
    print()

    # 7. Sentiment vs Length Analysis
    print("7. SENTIMENT AND REVIEW LENGTH CORRELATION:")
    print("-" * 50)
    correlation = notes_df["word_count"].corr(notes_df["compound_score"])
    print(f"Correlation coefficient: {correlation:.3f}")
    print("(1 = perfect positive correlation, -1 = perfect negative correlation)")
    print()

    # 8. Technical Issues Analysis
    print("8. MOST REPORTED TECHNICAL ISSUES:")
    print("-" * 50)
    technical_bigrams = [b for b in bigram_freq_data 
                        if any(word in b["bigram"].lower() 
                        for word in ["not working", "doesn work", "cant run", "black screen", 
                                   "crash game", "game crash", "no sound", "proton ge"])][:10]
    for bigram in technical_bigrams:
        print(f"- '{bigram['bigram']}': reported {bigram['frequency']} times")
    print()

    # Additional Statistics
    print("9. GENERAL STATISTICS:")
    print("-" * 50)
    print(f"Total number of reviews analyzed: {len(notes_df)}")
    print(f"Average words per review: {notes_df['word_count'].mean():.1f}")
    print(f"Average sentences per review: {notes_df['sentence_count'].mean():.1f}")
    print(f"Average lexical diversity: {notes_df['lexical_diversity'].mean():.3f}")
    print()

    # Visualisasi yang lebih bermakna untuk konteks ProtonDB
    vis_dir = f"{output_dir}/visualizations"
    os.makedirs(vis_dir, exist_ok=True)
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)

    # 1. Bar Plot: Distribusi Kategori Masalah
    plt.figure()
    topic_counts = notes_df["topic_category"].value_counts()
    sns.barplot(x=topic_counts.values, y=topic_counts.index, palette="RdYlGn_r")
    plt.title("Distribusi Kategori Masalah di ProtonDB", fontsize=14)
    plt.xlabel("Jumlah Laporan", fontsize=12)
    plt.ylabel("Kategori Masalah", fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/issue_categories_{timestamp}.png")
    plt.close()

    # 2. Pie Chart: Sentimen Pengguna terhadap Proton
    plt.figure()
    sentiment_counts = notes_df["sentiment"].value_counts()
    colors = {"positive": "#2ecc71", "neutral": "#f1c40f", "negative": "#e74c3c"}
    plt.pie(sentiment_counts, labels=sentiment_counts.index, 
            autopct="%1.1f%%", 
            colors=[colors[s] for s in sentiment_counts.index])
    plt.title("Sentimen Pengguna terhadap Kompatibilitas Proton", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/proton_sentiment_{timestamp}.png")
    plt.close()

    # 3. Bar Plot: Kata-kata Terkait Performa
    plt.figure()
    performance_words = ["fps", "performance", "smooth", "lag", "stutter", "slow", "fast", "run"]
    perf_freq = {w["word"]: w["frequency"] for w in word_freq_data if w["word"] in performance_words}
    if perf_freq:
        sns.barplot(x=list(perf_freq.values()), y=list(perf_freq.keys()), palette="YlOrRd")
        plt.title("Frekuensi Kata Terkait Performa Game", fontsize=14)
        plt.xlabel("Frekuensi", fontsize=12)
        plt.ylabel("Kata", fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{vis_dir}/performance_terms_{timestamp}.png")
    plt.close()

    # 4. Grouped Bar Plot: Distribusi POS Tags berdasarkan Sentimen
    plt.figure()
    pos_by_sentiment = notes_df.groupby("sentiment")[["noun_count", "verb_count", "adjective_count", "adverb_count"]].mean()
    pos_by_sentiment.plot(kind="bar", width=0.8)
    plt.title("Penggunaan Kata berdasarkan Sentimen Review", fontsize=14)
    plt.xlabel("Sentimen", fontsize=12)
    plt.ylabel("Rata-rata Jumlah Kata", fontsize=12)
    plt.legend(title="Jenis Kata")
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/pos_by_sentiment_{timestamp}.png")
    plt.close()

    # 5. Word Cloud berdasarkan Sentimen
    for sentiment in ["positive", "negative", "neutral"]:
        plt.figure(figsize=(10, 6))
        sentiment_tokens = " ".join(notes_df[notes_df["sentiment"] == sentiment]["tokens"])
        if sentiment_tokens.strip():
            color = "YlGn" if sentiment == "positive" else "Reds" if sentiment == "negative" else "Greys"
            wordcloud = WordCloud(width=800, height=400, 
                                background_color="white",
                                colormap=color).generate(sentiment_tokens)
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title(f"Kata-kata Umum dalam Review {sentiment.title()}", fontsize=14)
            plt.tight_layout()
            plt.savefig(f"{vis_dir}/wordcloud_{sentiment}_{timestamp}.png")
        plt.close()

    # 6. Box Plot: Panjang Review berdasarkan Kategori Masalah
    plt.figure()
    sns.boxplot(x="topic_category", y="word_count", data=notes_df, palette="Set3")
    plt.xticks(rotation=45, ha="right")
    plt.title("Panjang Review berdasarkan Kategori Masalah", fontsize=14)
    plt.xlabel("Kategori Masalah", fontsize=12)
    plt.ylabel("Jumlah Kata", fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/review_length_by_category_{timestamp}.png")
    plt.close()

    # 7. Scatter Plot: Hubungan Sentimen dengan Panjang Review
    plt.figure()
    sns.scatterplot(data=notes_df, x="word_count", y="compound_score", 
                    hue="topic_category", alpha=0.6)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)
    plt.title("Hubungan Panjang Review dengan Sentimen", fontsize=14)
    plt.xlabel("Jumlah Kata", fontsize=12)
    plt.ylabel("Skor Sentimen", fontsize=12)
    plt.legend(title="Kategori Masalah", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/sentiment_vs_length_{timestamp}.png")
    plt.close()

    # 8. Bar Plot: Bigram Terkait Masalah Teknis
    plt.figure()
    technical_bigrams = [b for b in bigram_freq_data 
                        if any(word in b["bigram"].lower() 
                        for word in ["not working", "doesn work", "cant run", "black screen", 
                                   "crash game", "game crash", "no sound", "proton ge"])][:10]
    if technical_bigrams:
        sns.barplot(x=[b["frequency"] for b in technical_bigrams], 
                   y=[b["bigram"] for b in technical_bigrams], 
                   palette="Reds_r")
        plt.title("Masalah Teknis yang Sering Dilaporkan", fontsize=14)
        plt.xlabel("Frekuensi", fontsize=12)
        plt.ylabel("Masalah", fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{vis_dir}/technical_issues_{timestamp}.png")
    plt.close()

    print("All visualizations saved in", vis_dir)
    print("Loading and visualization completed!")
    return output_dir
