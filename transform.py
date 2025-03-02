# transform.py
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag
from nltk.chunk import ne_chunk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
import json
import os

# Download resource NLTK yang diperlukan
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)
nltk.download('vader_lexicon', quiet=True)
nltk.download('wordnet', quiet=True)

def transform(games, all_reports):
    print("Starting transformation process with maximum NLTK analysis...")

    notes_file = "temp_notes.json"
    word_freq_file = "temp_word_freq.json"
    bigram_freq_file = "temp_bigram_freq.json"
    trigram_freq_file = "temp_trigram_freq.json"

    # Cek apakah data transformasi sudah ada
    if all(os.path.exists(f) for f in [notes_file, word_freq_file, bigram_freq_file, trigram_freq_file]):
        print("Loading existing transformed data from JSON files...")
        with open(notes_file, 'r') as nf:
            notes_data = json.load(nf)
        with open(word_freq_file, 'r') as wf:
            word_freq_data = json.load(wf)
        with open(bigram_freq_file, 'r') as bf:
            bigram_freq_data = json.load(bf)
        with open(trigram_freq_file, 'r') as tf:
            trigram_freq_data = json.load(tf)
        print(f"Loaded {len(notes_data)} notes from {notes_file}")
        return notes_data, word_freq_data, bigram_freq_data, trigram_freq_data

    # Jika tidak ada, lakukan transformasi
    notes_data = []
    all_words = []
    all_bigrams = []
    all_trigrams = []

    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    sid = SentimentIntensityAnalyzer()

    topic_keywords = {
        "performance": {"lag", "slow", "fast", "smooth", "runs", "fps"},
        "bugs": {"crash", "bug", "error", "broken", "fail"},
        "compatibility": {"works", "support", "compatible", "install"}
    }

    for game in games:
        app_id = game["appId"]
        reports = all_reports.get(app_id, [])

        if not reports:
            continue

        for report in reports:
            # Fix: Check if report is None first
            if report is None:
                continue
                
            # Fix: Safely get notes field and check if it's None
            notes = report.get("notes")
            if notes is None:
                continue
                
            # Now safely call strip()
            notes = notes.strip()
            if not notes:
                continue

            sentences = sent_tokenize(notes)
            tokens = word_tokenize(notes.lower())
            clean_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
            
            # Prevent division by zero
            word_count = len(clean_tokens)
            if word_count == 0:
                continue
                
            char_count = len(notes)
            sentence_count = len(sentences)
            avg_word_length = sum(len(word) for word in clean_tokens) / word_count if word_count > 0 else 0

            stemmed_tokens = [ps.stem(token) for token in clean_tokens]
            lemmatized_tokens = [lemmatizer.lemmatize(token) for token in clean_tokens]

            pos_tags = pos_tag(clean_tokens)
            pos_counts = Counter(tag for word, tag in pos_tags)

            ner_tree = ne_chunk(pos_tags)
            entities = []
            for subtree in ner_tree:
                if isinstance(subtree, nltk.Tree):
                    entity = " ".join(word for word, tag in subtree.leaves())
                    entities.append({"entity": entity, "label": subtree.label()})

            sentiment_scores = sid.polarity_scores(notes)
            sentiment = "positive" if sentiment_scores["compound"] > 0.05 else "negative" if sentiment_scores["compound"] < -0.05 else "neutral"

            bigrams = list(nltk.bigrams(clean_tokens))
            trigrams = list(nltk.trigrams(clean_tokens))
            all_bigrams.extend(bigrams)
            all_trigrams.extend(trigrams)

            unique_words = len(set(clean_tokens))
            lexical_diversity = unique_words / word_count if word_count > 0 else 0

            topics = []
            for topic, keywords in topic_keywords.items():
                if any(keyword in clean_tokens for keyword in keywords):
                    topics.append(topic)
            topic_category = ", ".join(topics) if topics else "other"

            notes_data.append({
                "note_text": notes,
                "word_count": word_count,
                "char_count": char_count,
                "sentence_count": sentence_count,
                "avg_word_length": avg_word_length,
                "lexical_diversity": lexical_diversity,
                "tokens": " ".join(clean_tokens),
                "stemmed_tokens": " ".join(stemmed_tokens),
                "lemmatized_tokens": " ".join(lemmatized_tokens),
                "noun_count": pos_counts.get("NN", 0) + pos_counts.get("NNS", 0),
                "verb_count": pos_counts.get("VB", 0) + pos_counts.get("VBD", 0) + pos_counts.get("VBG", 0),
                "adjective_count": pos_counts.get("JJ", 0),
                "adverb_count": pos_counts.get("RB", 0),
                "entities": json.dumps(entities),
                "sentiment": sentiment,
                "compound_score": sentiment_scores["compound"],
                "positive_score": sentiment_scores["pos"],
                "negative_score": sentiment_scores["neg"],
                "neutral_score": sentiment_scores["neu"],
                "topic_category": topic_category
            })
            all_words.extend(clean_tokens)

    word_freq = Counter(all_words)
    bigram_freq = Counter(all_bigrams)
    trigram_freq = Counter(all_trigrams)
    word_freq_data = [{"word": word, "frequency": freq} for word, freq in word_freq.most_common()]
    bigram_freq_data = [{"bigram": " ".join(bigram), "frequency": freq} for bigram, freq in bigram_freq.most_common()]
    trigram_freq_data = [{"trigram": " ".join(trigram), "frequency": freq} for trigram, freq in trigram_freq.most_common()]

    # Simpan ke file JSON sementara
    with open(notes_file, 'w') as nf:
        json.dump(notes_data, nf)
    with open(word_freq_file, 'w') as wf:
        json.dump(word_freq_data, wf)
    with open(bigram_freq_file, 'w') as bf:
        json.dump(bigram_freq_data, bf)
    with open(trigram_freq_file, 'w') as tf:
        json.dump(trigram_freq_data, tf)
    print(f"Transformed data saved to {notes_file}, {word_freq_file}, {bigram_freq_file}, {trigram_freq_file}")
    print("Transformation completed!")
    return notes_data, word_freq_data, bigram_freq_data, trigram_freq_data