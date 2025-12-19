import os
import numpy as np
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import nltk

# Download the necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Directory paths for each chatbot's documents
directories = {
    "Customer Database Search": "../chatbot_documents/customer_database_search",
    "Organizational Information": "../chatbot_documents/organizational_information",
    "Internet Search": "../chatbot_documents/internet_search"
}

# Define additional common words to exclude (custom stopwords)
custom_stop_words = set([
    "may", "would", "could", "also", "one", "two", "three", "many", "first", "second", 
    "must", "often", "much", "time", "include", "help", "information", "title"
])

# Function to preprocess the text
def preprocess_text(text):
    # Tokenize the text and remove both default and custom stopwords
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english')).union(custom_stop_words)
    return [word for word in tokens if word.isalpha() and word not in stop_words]

# Collect word counts across all bot directories to identify common words
def get_word_counts(directories):
    global_counter = Counter()
    for dir_path in directories.values():
        for filename in os.listdir(dir_path):
            if filename.endswith('.txt'):
                with open(os.path.join(dir_path, filename), 'r', encoding='utf-8') as file:
                    words = preprocess_text(file.read())
                    global_counter.update(words)
    return global_counter

# Get and filter out common words based on global frequency
global_word_counts = get_word_counts(directories)
common_word_threshold = 3  # Appear across all bot directories
common_words = {word for word, count in global_word_counts.items() if count >= common_word_threshold}

# Function to get most representative words using Word2Vec, filtered by specificity
def get_most_representative_words(directory, top_n=20):
    documents = []
    stop_words = set(stopwords.words('english')).union(custom_stop_words).union(common_words)

    # Read all text files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                documents.append(preprocess_text(file.read()))

    # Train Word2Vec model with a minimum word frequency (min_count) of 2
    model = Word2Vec(sentences=documents, vector_size=100, window=5, min_count=2, workers=4)
    
    # Calculate the average vector for all words, excluding common and stop words
    average_vector = np.mean(
        [model.wv[word] for word in model.wv.index_to_key if word not in stop_words],
        axis=0
    )

    # Find the most similar words to the average vector
    similar_words = model.wv.similar_by_vector(average_vector, topn=top_n)
    
    # Filter out any remaining common and stop words from the results
    filtered_similar_words = [(word, similarity) for word, similarity in similar_words if word not in stop_words]
    
    return filtered_similar_words

# Generate the Word2Vec representation for each bot and store in a dictionary
bot_representations = {}
for bot_name, dir_path in directories.items():
    representative_words = get_most_representative_words(dir_path)
    bot_representations[bot_name] = {word: float(similarity) for word, similarity in representative_words}

# Save the representations to a JSON file

output_file = "metadata/bot_word2vec_representations.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(bot_representations, f, ensure_ascii=False, indent=2)

print(f"Word2Vec representations have been saved to {output_file}")
