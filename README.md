# ProtonDB ETL Pipeline

The **ProtonDB ETL Pipeline** is a Python-based application designed to extract, transform, and load data from ProtonDB (a community-driven database for game compatibility with Proton on Linux). This tool fetches game and report data from the ProtonDB API, processes it using natural language processing (NLP) techniques with NLTK, and stores the results in CSV files, a SQLite database, and visualizations for detailed analysis.

## Features
- **Extract**: Retrieves game metadata and user reports from the ProtonDB API.
- **Transform**: Processes user reports with extensive NLP analysis (tokenization, stemming, lemmatization, sentiment analysis, POS tagging, named entity recognition, etc.).
- **Load**: Saves processed data into structured formats (CSV, SQLite) and generates insightful visualizations (bar plots, pie charts, word clouds, etc.).
- **Caching**: Uses temporary JSON files to avoid redundant API calls or reprocessing.
- **Interactive Menu**: Provides a simple command-line interface to run the ETL pipeline step-by-step.

## Prerequisites
Before running the program, ensure you have the following installed:
- Python 3.8 or higher
- Required Python packages (install via `pip`):
  ```bash
  pip install requests nltk pandas sqlite3 matplotlib seaborn wordcloud numpy
  ```
- NLTK resources (downloaded automatically by the script on first run):
  - `punkt`
  - `stopwords`
  - `averaged_perceptron_tagger`
  - `maxent_ne_chunker`
  - `words`
  - `vader_lexicon`
  - `wordnet`

## Installation
1. Clone or download this repository:
   ```bash
   git clone https://github.com/username/protondb-etl-pipeline.git
   cd protondb-etl-pipeline
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (Create a `requirements.txt` with the packages listed above if not already included.)

3. Run the program:
   ```bash
   python main.py
   ```

## Usage
The program provides an interactive menu with the following options:
1. **Extract Data**: Fetches game and report data from ProtonDB. You can specify a limit for the number of games or leave it blank to process all available games.
2. **Transform Data**: Processes the extracted reports using NLP techniques. Requires extracted data to be available (either from step 1 or cached files).
3. **Load Data (and Visualization)**: Saves the transformed data into CSV files and a SQLite database, then generates visualizations in a timestamped output directory.
0. **Exit**: Terminates the program.

### Example Workflow
```bash
python main.py
```
- Select `1` and enter a limit (e.g., `10`) or press Enter for all games.
- Select `2` to transform the extracted data.
- Select `3` to load the data and generate visualizations.
- Check the `output_<timestamp>` directory for results.

## File Structure
- **`main.py`**: Entry point of the program with the interactive menu and ETL orchestration.
- **`extract.py`**: Handles data extraction from the ProtonDB API and caching to temporary JSON files (`temp_games.json`, `temp_reports.json`).
- **`transform.py`**: Performs NLP-based transformation of user reports, including sentiment analysis, tokenization, and frequency analysis. Results are cached in `temp_notes.json`, `temp_word_freq.json`, `temp_bigram_freq.json`, and `temp_trigram_freq.json`.
- **`load.py`**: Loads transformed data into CSV files, a SQLite database, and generates visualizations (bar plots, pie charts, word clouds, etc.) in an `output_<timestamp>/visualizations` directory.

### Temporary Files
- `temp_games.json`: Cached game metadata.
- `temp_reports.json`: Cached user reports.
- `temp_notes.json`: Cached transformed notes data.
- `temp_word_freq.json`: Cached word frequency data.
- `temp_bigram_freq.json`: Cached bigram frequency data.
- `temp_trigram_freq.json`: Cached trigram frequency data.

### Output Files
Generated in `output_<timestamp>/`:
- `protondb_notes_<timestamp>.csv`: Processed notes data.
- `protondb_word_freq_<timestamp>.csv`: Word frequency data.
- `protondb_bigram_freq_<timestamp>.csv`: Bigram frequency data.
- `protondb_trigram_freq_<timestamp>.csv`: Trigram frequency data.
- `protondb_notes_analysis_<timestamp>.db`: SQLite database with all tables.
- `visualizations/`: Directory containing PNG files of visualizations.

## Data Processing Details
### Extraction
- Fetches game metadata from `https://protondb.max-p.me/games/`.
- Fetches reports for each game from `https://protondb.max-p.me/games/<appId>/reports/`.
- Stores raw data in temporary JSON files to avoid repeated API calls.

### Transformation
- Uses NLTK for:
  - **Tokenization**: Splits text into words and sentences.
  - **Stopword Removal**: Removes common English stopwords.
  - **Stemming**: Applies Porter Stemmer to reduce words to their root form.
  - **Lemmatization**: Uses WordNet Lemmatizer for word normalization.
  - **POS Tagging**: Identifies parts of speech (nouns, verbs, adjectives, etc.).
  - **Named Entity Recognition (NER)**: Extracts entities like names or organizations.
  - **Sentiment Analysis**: Uses VADER to classify sentiment as positive, neutral, or negative.
  - **N-gram Analysis**: Computes word, bigram, and trigram frequencies.
- Categorizes reports into topics (performance, bugs, compatibility) based on keyword matching.
- Computes lexical diversity, word counts, and other text statistics.

### Loading
- Stores data in:
  - **CSV**: For easy access and analysis in tools like Excel or pandas.
  - **SQLite**: For structured querying with tables `notes`, `word_freq`, `bigram_freq`, and `trigram_freq`.
- Generates visualizations:
  1. Issue category distribution (bar plot).
  2. User sentiment distribution (pie chart).
  3. Performance-related term frequency (bar plot).
  4. POS usage by sentiment (grouped bar plot).
  5. Word clouds by sentiment.
  6. Review length by category (box plot).
  7. Sentiment vs. review length (scatter plot).
  8. Technical issue bigrams (bar plot).

## Analysis Output
The `load.py` script prints detailed analysis results, including:
1. Distribution of issue categories (e.g., performance, bugs).
2. Sentiment analysis (positive/negative/neutral percentages).
3. Frequency of performance-related terms.
4. Language usage (POS counts) by sentiment.
5. Most common words by sentiment.
6. Review length statistics by category.
7. Correlation between sentiment and review length.
8. Most reported technical issues (based on bigrams).
9. General statistics (e.g., total reviews, average word count).

## Limitations
- Requires an internet connection for initial data extraction.
- API rate limits or downtime may affect extraction.
- Large datasets may consume significant memory and processing time.
- Visualizations assume sufficient data; sparse datasets may produce less meaningful plots.

## Contributing
Feel free to submit issues or pull requests to enhance functionality, such as:
- Adding more topic categories or keywords.
- Improving visualization aesthetics or adding new plot types.
- Optimizing performance for large datasets.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- Built with Python, NLTK, pandas, matplotlib, seaborn, and other open-source libraries.
- Data sourced from [ProtonDB](https://protondb.max-p.me/).
- Inspired by the need to analyze game compatibility on Linux via Proton.

---