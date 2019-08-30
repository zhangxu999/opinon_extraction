# -*- coding: utf-8 -*-
import sys
from pyltp import Segmentor  # pyltp 提供分词、词性标注、命名实体识别、依存句法分析、语义角色标注等功能。
from pyltp import SentenceSplitter
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
import os
from utils.load_data import load_synonyms
from config import SYNONYMS_PATH, LTP_MODEL_PATH

from model.speech import TfidfDecisionMaker, Word2vecDecisionMaker
from utils import write_a_log
class LTPManager:
    """
    有关LTP语言包的函数和方法
    """

    def __init__(self, data_dir):
        self.LTP_DATA_DIR = data_dir
        cws_model_path = os.path.join(self.LTP_DATA_DIR, 'cws.model')
        # 分词模型路径，分词模型名称是‘cws.model’
        self.segmentor = Segmentor()
        self.segmentor.load(cws_model_path)

        pos_model_path = os.path.join(self.LTP_DATA_DIR, 'pos.model')
        # 词性标注模型路径，分词模型名称是‘pos.model’
        self.postagger = Postagger()
        self.postagger.load(pos_model_path)

        ner_model_path = os.path.join(self.LTP_DATA_DIR, 'ner.model')
        self.recognizer = NamedEntityRecognizer()
        self.recognizer.load(ner_model_path)

        par_model_path = os.path.join(self.LTP_DATA_DIR, 'parser.model')
        self.parser = Parser()
        self.parser.load(par_model_path)

    def split_sentences(self, sentence):
        sen = SentenceSplitter.split(sentence)
        sentences = [s for s in sen if s]
        return sentences

    def split_words(self, words):
        words = self.segmentor.segment(words)

        return words

    def get_sentence_pos(self, words):
        """
        词性标注
        :return:
        """
        postags = self.postagger.postag(words)
        return postags

    def NER(self, words, postags):
        """
        命名实体识别
        """

        netags = self.recognizer.recognize(words, postags)
        return netags

    def dependency_parsing(self, words, postags):
        """
        依存句法分析。
        """
        arcs = self.parser.parse(words, postags)
        return arcs


class SpeechExtractor:
    def __init__(self, synonyms_path, ltp_manager):
        self.synonyms = set(load_synonyms(synonyms_path))
        self.ner_set = set(['S-Nh', 'S-Ni', 'S-Ns'])
        self.ltp_manager = ltp_manager

    def who_say_what(self, words):
        """
        对单句提取新闻人物和言论.
        :return:
        """
        content = []
        # words = self.ltp_manager.split_words(sentence)
        matched_synonyms = set(words) & self.synonyms
        if matched_synonyms:
            # 判断句子中是否存在synonyms
            postags = self.ltp_manager.get_sentence_pos(words)
            netags = self.ltp_manager.NER(words, postags)
            write_a_log('who_say_what','postags',list(postags))
            write_a_log('who_say_what','netags',list(netags))
            if set(netags) & self.ner_set:
                # 判断句子中是否存在NER实体，我怀疑这一句是否有效
                arcs = self.ltp_manager.dependency_parsing(words, postags)
                arcs = [(i, arc.head - 1, arc.relation) for i, arc in enumerate(arcs) if arc.relation == 'SBV']
                for i, head_idx, relation in arcs:
                    subject, head = words[i], words[head_idx]
                    if head in matched_synonyms:
                        content = [subject, head, ''.join(words[head_idx+1:])]
                        break
                        #发现一个触发次，就不再往下找了。
        return content

    def get_speech(self, para, finalize_method, alpha):
        # Get someone's speech from a paragraph
        result = list()
        para =  para.replace('\\n','').replace('\u3000','')
        split_sentence = self.ltp_manager.split_sentences(para)
        segmented_docs = [self.ltp_manager.segmentor.segment(s) for s in split_sentence]
        write_a_log('get_speech','segmented_docs',segmented_docs)
        decision_maker = None
        for i, sen in enumerate(segmented_docs):
            content = self.who_say_what(sen)
            if not content:
                continue
            if decision_maker is None:
                # print('finalize_method:::::',finalize_method)
                decision_maker = TfidfDecisionMaker \
                    if finalize_method == 'select_tfidf' else Word2vecDecisionMaker
                decision_maker = decision_maker(segmented_docs,alpha=alpha)
            end_index,similaritys = decision_maker.get_end_index(i)
            if end_index != i:
                content[2] += ''.join([sen for sen in split_sentence[i+1:end_index+1]])
            result.extend([content])
        return result

    def get_speech_from_file(self, file_name):
        # Get someone's speech from a file
        result = list()
        with open(file_name, 'r+', encoding='utf-8') as file:
            for line in file:
                content = self.who_say_what(line)
                if content:
                    result.extend(speech)
        return result

LTPM = LTPManager(data_dir=LTP_MODEL_PATH)
SE = SpeechExtractor(synonyms_path=SYNONYMS_PATH, ltp_manager=LTPM)


def get_speech(para,finalize_method, alpha):
    return SE.get_speech(para,finalize_method,alpha)


test_doc = """
新华社香港8月11日电 香港升旗队总会11日在新界元朗一家中学举行“家在中华”升旗礼，吸引多名市民参与。

习近平先生也说过这是一件重要的事情。

正午时分，艳阳高照。由香港多家中学组成的升旗队伍，护送国旗到学校操场的旗杆下。五星红旗伴随着国歌冉冉升起，气氛庄严。
香港升旗队总会主席周世耀在国旗下致辞时表示，最近香港发生很多不愉快的事件，包括部分人侮辱国旗国徽、挑战“一国两制”原则底线，也分化了香港和内地的同胞。希望通过当天举行升旗活动弘扬正能量，并传递一个重要讯息：香港属于中华民族大家庭。

香港升旗队总会总监许振隆勉励年轻人说，要关心社会，关心国家，希望年轻人以国为荣，为国争光。
活动接近尾声，参与者在中国地图上贴上中国国旗，象征大家共同努力建设国家。最后，全体人员合唱《明天会更好》，为香港送上美好祝愿。

今年15岁的郭紫晴在香港土生土长。她表示，这次升旗礼是特别为香港加油而举行的，希望大家都懂得尊重自己的国家。“看着国旗升起，想到自己在中国这片土地上成长，感到十分自豪。”
“升旗仪式(与以往)一样，但意义却不同。”作为当天升旗队成员之一的高中生赵颖贤说，国旗和国徽代表了一个国家的尊严，不容践踏，很期望当天的活动能向广大市民传达这一信息。

即将升读初三的蒋靖轩认为，近日香港发生连串暴力事件，当天的升旗仪式更显意义，希望香港快快恢复平静，港人都团结起来。

"""

if __name__ == '__main__':
    from config import SYNONYMS_PATH, LTP_MODEL_PATH
    LTPM = LTPManager(data_dir='../' + LTP_MODEL_PATH)
    SE = SpeechExtractor(synonyms_path='../' + SYNONYMS_PATH, ltp_manager=LTPM)
    speech = SE.get_speech(test_doc)
    print(speech)
