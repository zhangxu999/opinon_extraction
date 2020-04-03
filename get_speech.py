# -*- coding: utf-8 -*-
import sys
# from pyltp import Segmentor  # pyltp 提供分词、词性标注、命名实体识别、依存句法分析、语义角色标注等功能。
# from pyltp import SentenceSplitter
# from pyltp import Postagger
# from pyltp import NamedEntityRecognizer
# from pyltp import Parser
from pyhanlp import HanLP
import os
from collections import defaultdict
from utils.load_data import load_synonyms
from config import SYNONYMS_PATH, LTP_MODEL_PATH
from pyhanlp import *

custom_words = """
冠状病毒 肺炎 武汉 湖北 湖北省 黄冈 孝感 感染 诊断 病毒 SARS 非典 
疫情 确诊 病例 疑似病例 防控 医院 卫健委 卫生健康委 卫生健康委员会 WHO 世界卫生组织 
传染病 N95 口罩 新型冠状病毒 病原 野生动物 蝙蝠 果子狸 患者 病例 体温
防护服 发热 门诊 埃博拉 华南海鲜市场 交叉 感染 捐赠
""".split()
CustomDictionary = JClass("com.hankcs.hanlp.dictionary.CustomDictionary")
for w in custom_words:
    CustomDictionary.add(w)  # 动态增加

from model.speech import TfidfDecisionMaker, Word2vecDecisionMaker
from utils import write_a_log
class LTPManager:
    """
    有关LTP语言包的函数和方法
    """

    def __init__(self, data_dir):
        self.LTP_DATA_DIR = data_dir
        # cws_model_path = os.path.join(self.LTP_DATA_DIR, 'cws.model')
        # # 分词模型路径，分词模型名称是‘cws.model’
        # self.segmentor = Segmentor()
        # self.segmentor.load(cws_model_path)
        #
        # pos_model_path = os.path.join(self.LTP_DATA_DIR, 'pos.model')
        # # 词性标注模型路径，分词模型名称是‘pos.model’
        # self.postagger = Postagger()
        # self.postagger.load(pos_model_path)
        #
        # ner_model_path = os.path.join(self.LTP_DATA_DIR, 'ner.model')
        # self.recognizer = NamedEntityRecognizer()
        # self.recognizer.load(ner_model_path)
        #
        # par_model_path = os.path.join(self.LTP_DATA_DIR, 'parser.model')
        # self.parser = Parser()
        # self.parser.load(par_model_path)

    def split_sentences(self, document):
        all_sentences = []
        for text in document.split('\n'):
            sen_begin = 0
            cnt = len(text)
            for i in range(cnt):
                if text[i] in ['。', '?', '？', '！', '!']:
                    all_sentences.append(text[sen_begin:i + 1])
                    sen_begin = i + 1
                if text[i] == '.':
                    if text[i+1:i + 2].isdigit():
                        continue
                    else:
                        all_sentences.append(text[sen_begin:i])
                        sen_begin = i + 1
            if sen_begin <= i:
                all_sentences.append(text[sen_begin:i+1])
        return all_sentences

    def split_words(self, sentence):
        seg_words = HanLP.segment(sentence)
        words = [w.word for w in seg_words]
        nature = [w.nature.toString() for w in seg_words]

        return words, nature

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
        words = HanLP.parseDependency(''.join(words))
        # arcs = self.parser.parse(words, postags)
        return list(words)


class SpeechExtractor:
    def __init__(self, synonyms_path, ltp_manager):
        self.synonyms = set(load_synonyms(synonyms_path))
        self.ner_set = set(['nr', 'nt', 'nz', 'nx', 'ns', 'ni'])
        self.ltp_manager = ltp_manager
        self.word_tag_level = {'nrf':101,'nr':100,'nt':98,'nh':96,'nn':95,'n':93,'j':92,'r':90,'l':85,'s':80,'vn':73,'v':70,}

    def get_full_entity(self, arcs,entity_index):
        part_arcs = arcs[:entity_index]
        core_entity = arcs[entity_index]
        full_entity = ''
        tree = defaultdict(list)
        is_entity = [0]*(entity_index)
        # is_entity[entity_index] = 1
        stack = [entity_index]
        for i,arc in enumerate(part_arcs):
            if (arc.DEPREL=='定中关系'):
                tree[arc.HEAD.ID-1].append(arc.ID-1)
        while stack:
            seed = stack.pop(0)
            for e in tree.get(seed,[]):
                is_entity[e] = 1
                stack.append(e)
        full_entity = ''.join([arc.LEMMA for arc in part_arcs if is_entity[arc.ID-1]])
        position = [arc.ID-1 for arc in part_arcs if is_entity[arc.ID-1]]
        full_entity += core_entity.LEMMA
        position.append(entity_index)
        return full_entity,position


        for i,arc in enumerate(arcs[:entity_index]):
            if (arc.DEPREL=='定中关系') and (arc.HEAD.ID == core_entity.ID):
                full_entity += arc.LEMMA
                postion.append(i)
        full_entity += core_entity.LEMMA 
        postion.append(core_entity.ID-1)
        return full_entity,postion

    def get_epidemic_num(self,segment_words):
        return len([w for words,nature in segment_words for w in words if w in custom_words])


    def who_say_what(self, words, nature,need_parse=True):
        """
        对单句提取新闻人物和言论.
        :return: content
        """
        content = {
            'dependency_parsing':'',
            'speech':[]
        }
        # words = self.ltp_manager.split_words(sentence)
        matched_synonyms = set(words) & self.synonyms
        nature_2 = [p[:2] for p in nature]
        have_ner = bool(set(nature_2)&self.ner_set)
        if matched_synonyms and have_ner:
            # 判断句子中是否存在synonyms # 判断句子中是否存在NER实体，我怀疑这一句是否有效
            arcs = self.ltp_manager.dependency_parsing(words, nature)
            # arcs = [(i, arc.HEAD, arc.DEPREL) for i, arc in enumerate(arcs) if arc.DEPREL == '主谓关系']
            arc,best_score = None,-1
            for a  in arcs:
                if (a.HEAD.LEMMA in matched_synonyms and a.DEPREL=='主谓关系'):
                    for i in range(len(a.POSTAG),0,-1):
                        score = self.word_tag_level.get(a.POSTAG[:i].lower(),0)
                        if score == 0:
                            print(f'{a.LEMMA}({a.POSTAG},{a.POSTAG[:i]})--> {a.HEAD.LEMMA}')
                        if score > best_score:
                            arc,best_score = a,score
            # for arc in arcs:
            if arc:
                start_idx = arc.HEAD.ID
                while (start_idx <len(arcs)) and arcs[start_idx].POSTAG.startswith('w'):
                    start_idx += 1
                opinoin = ''.join([i.LEMMA for i in arcs if i.ID > start_idx])
                full_entity,entity_positon = self.get_full_entity(arcs,arc.ID-1)
                speech = [full_entity, arc.HEAD.LEMMA, opinoin,arc.LEMMA, arc.POSTAG]
                speech_position = {
                    'entity':entity_positon,
                    'talk_word':[arc.HEAD.ID-1],
                    'speech':list(range(start_idx,len(arcs)))
                }
                content['speech'] = speech
                content['position'] = speech_position
            # dependency_str = [arc.toString() for arc in arcs]
            # content['dependency_parsing'] = dependency_str
        # if (content['dependency_parsing'] == '') and need_parse:
        content['dependency_parsing'] = [arc.toString() for arc in self.ltp_manager.dependency_parsing(words, nature)]
        return content

    def get_speech(self, para, finalize_method, alpha):
        # Get someone's speech from a paragraph
        result = list()
        para =  para.replace('\\n','').replace('\u3000','')
        split_sentence = self.ltp_manager.split_sentences(para)
        segmented_docs = [self.ltp_manager.split_words(s) for s in split_sentence]
        decision_maker = None
        for i, (sen,nature) in enumerate(segmented_docs):
            full_content = self.who_say_what(sen, nature)
            content = full_content['speech']
            if not content:
                result.extend([full_content])
                continue
            if decision_maker is None:
                # print('finalize_method:::::',finalize_method)
                decision_maker = TfidfDecisionMaker \
                    if finalize_method == 'select_tfidf' else Word2vecDecisionMaker
                only_seg_docs = [a for a,b in segmented_docs]
                decision_maker = decision_maker(only_seg_docs, alpha=alpha)
            end_index,similaritys = decision_maker.get_end_index(i)
            if end_index != i:
                content[2] += ''.join([sen for sen in split_sentence[i+1:end_index+1]])
                full_content['speech'] = content
            result.extend([full_content])
        epidemic_words_num = self.get_epidemic_num(segmented_docs)

        return_doc = {'speech':result,'epidemic_words_num':epidemic_words_num}
        return return_doc

    def get_speech_from_file(self, file_name):
        # Get someone's speech from a file
        result = list()
        with open(file_name, 'r+', encoding='utf-8') as file:
            for line in file:
                content = self.who_say_what(line)
                if content:
                    result.extend(speech)
        return result

# LTPM = LTPManager(data_dir=LTP_MODEL_PATH)
# SE = SpeechExtractor(synonyms_path=SYNONYMS_PATH, ltp_manager=LTPM)


def get_speech(para,finalize_method, alpha):
    return SE.get_speech(para,finalize_method,alpha)



import zmq
import json
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")
import logging
logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    from config import SYNONYMS_PATH, LTP_MODEL_PATH
    LTPM = LTPManager(data_dir=LTP_MODEL_PATH)
    SE = SpeechExtractor(synonyms_path=SYNONYMS_PATH, ltp_manager=LTPM)
    logger.info("加载完毕，开始接收消息....")
    while True:
        document = socket.recv().decode('utf8')
        document = json.loads(document)
        content = document['content']
        logger.info('receive message:{}'.format(content[:20]))
        # title = document['title']
        method = document['method']
        alpha = document['alpha']
        return_doc = SE.get_speech(content,method, alpha)
        logger.info('return speechs:{}'.format(str(return_doc)[:30]))
        return_doc = json.dumps(return_doc).encode('utf8')
        socket.send(return_doc)