# -*- coding: utf-8 -*-
from gensim.models import Word2Vec
from gensim.models.word2vec import PathLineSentences
import os
import time
from config import PROCESSED_DATA_PATH, WORD2VEC_MODEL_PATH

def train_word2vec_model(path):
    """
    训练词向量
    """
    if os.path.exists(path):
        print('Train Word2Vec model using all files under ', path)
        model = Word2Vec(PathLineSentences(path), min_count = 10, sg = 0, size = 128, window = 20, workers = 4) # CBOW model
        print(model.most_similar('说', topn=20))
    else:
        print(path, ' does not exit')
    return model


start = time.time()
word2vec_model = train_word2vec_model('../../' + PROCESSED_DATA_PATH)
end = time.time()
print(end-start)

word_vector = word2vec_model.wv
del word2vec_model
word_vector.save('../../' + WORD2VEC_MODEL_PATH)