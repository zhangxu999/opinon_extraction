from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import  cosine_similarity
from utils.load_data import load_stopwords
STOPWORDS = load_stopwords()
class TfidfDecisimMaker:
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
        print(''.join(self.sentences[sen_index]))
        check_indices = range(sen_index+1,min(self.doc_length, sen_index+self.max_length+1))
        for i in check_indices:
            similarity = cosine_similarity(base_vector, self.tfidf_X[i])
            if similarity[0][0] > self.alpha:
                print(similarity[0][0],''.join(self.sentences[i]))
                end_index = i
            else:
                break
        return end_index 


        