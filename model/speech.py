# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import  cosine_similarity
from utils.load_data import load_stopwords
from gensim.models import KeyedVectors
import numpy as np
from utils import write_a_log
from config import WORD2VER_MODEL_PATH
word2vec_model = KeyedVectors.load(WORD2VER_MODEL_PATH, mmap='r')

STOPWORDS = load_stopwords()

class TfidfDecisionMaker:
    """
    将句子使用TFIDF向量化表示，判断相邻两句的cosine 相似度。相似度小于某一阈值，认为相邻的两句不相关。可以断句
    """

    def __init__(self,segmented_sentences, alpha=0.1, max_length=3):
        self.sentences = segmented_sentences
        self.alpha = alpha
        self.max_length = max_length

        self.vectorizer = TfidfVectorizer(analyzer=self.clean_words)
        #print(self.sentences)
        self.tfidf_X = self.vectorizer.fit_transform(self.sentences)
        self.doc_length = len(segmented_sentences)
        

    @staticmethod
    def clean_words(sen):
#         print(sen)
        return [s for s in sen if s not in STOPWORDS]

    def get_end_index(self,sen_index):
        base_vector = self.tfidf_X[sen_index]
        end_index = sen_index
        check_indices = range(sen_index+1,min(self.doc_length, sen_index+self.max_length+1))
        similaritys = []
        for i in check_indices:
            similarity = cosine_similarity(base_vector.reshape(1,-1), self.tfidf_X[i].reshape(1,-1))
            if similarity[0][0] > self.alpha:
                end_index = i
                similaritys.append(similarity[0][0])
            else:
                break
        write_a_log('DecisionMaker','get_end_index',similaritys)
        return end_index ,similaritys

class Word2vecDecisionMaker(TfidfDecisionMaker):
    def __init__(self,segmented_sentences, alpha=0.1, max_length=3):
        self.sentences = segmented_sentences
        self.alpha = alpha
        self.max_length = max_length
        self.vec_size = word2vec_model.vector_size
        def calc_sen_vector(sen):
            all_vec = [word2vec_model[w] if w in word2vec_model else np.zeros(self.vec_size) for w in sen]
            return np.average(all_vec,axis=0)
        self.tfidf_X = np.array([calc_sen_vector(sen) for sen in self.sentences])

        # self.vectorizer = TfidfVectorizer(analyzer=self.clean_words)
        # #print(self.sentences)
        # self.tfidf_X = self.vectorizer.fit_transform(self.sentences)
        self.doc_length = len(segmented_sentences)


        
