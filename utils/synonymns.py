import os
def load_synonyms(file_name):
    print(file_name)
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            synonyms = f.readline().split('|')
        print(synonyms)
        return synonyms
