import os
from config import DEFAULT_STOPWORDS_PATH
def load_synonyms(file_name):
    print(file_name)
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            synonyms = f.readline().split('|')
        return synonyms
def load_stopwords(file_name=None):
    if file_name is None:
        file_name = DEFAULT_STOPWORDS_PATH
    with open(file_name) as f:
        stopwords = set(line[:-1] for line in f)
    return stopwords