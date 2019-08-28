from collections import defaultdict

import time

import sys
sys.path.append('../..')

### 导入gensim word2vec 模型

from gensim.models import Word2Vec
from gensim.models.word2vec import PathLineSentences,LineSentence
from gensim.models import KeyedVectors
import os
import numpy as np
from functools import  reduce, lru_cache
from collections import Counter
word_vector = KeyedVectors.load('../../data/word2vec100.wv', mmap='r')

@lru_cache(maxsize=2048)
def get_related_word(init,level):
    if level == 0:
        dist = np.average(word_vector.distances(init,seed))
        return Counter({init:dist})
    children = [w for w,simi in word_vector.most_similar(init,topn=5)] if isinstance(init,str) else init

    sub_result = reduce(lambda x,y:x+y,[get_related_word(w,level-1) for w in children])
    if isinstance(init,str):
        dist = np.average(word_vector.distances(init,seed))
        own_result = Counter({init:dist}) 
    else:
        own_result = Counter({k:np.average(word_vector.distances(k,seed)) for k in init})
    return sub_result+own_result

seed = ['说','否认','坚称','回应','告诉','反驳','承认','时说','批评','驳斥','质疑','议论','宣称','诋毁','答道','回答','嘲讽',
       '写道','争辩','指出','指证','承认']

level_seen = get_related_word(tuple(seed),6)

sort_v = sorted([(k,v) for k,v in level_seen.items()],reverse=True,key=lambda x:x[1])

print([k for k,v in sort_v[:200]])

'''
['坚称', '否认', '质疑', '问道', '辩解', '声称', '纯属', '问', '反驳', '辩称', '批评', '回答', '答道', '澄清', '指责', '说', '回应', '抨击', '严厉批评', '诋毁', '嘲讽', '说道', '嘲弄', '对此', '知情', '属实', '怎能', '蔑视', '指出', '致歉', '地问', '道歉', '问起', '谈到', '讽刺', '说完', '污蔑', '嘲笑', '指摘', '谴责', '提问', '真的', '申辩', '忍不住', '询问', '驳斥', '宣称', '报道', '回覆', '批评者', '论断', '发问', '歉意', '却说', '不知情', '轻蔑', '高估', '要说', '观点', '引述', '抱歉', '低估', '表示歉意', '报导', '毫无根据', '这番话', '听后', '挖苦', '问到', '论点', '岂能', '问及', '惭愧', '想', '很棒', '告知', '谈及', '这话', '论据', '毫无疑问', '进谏', '鄙视', '知悉', '看法', '祸乱', '查证', '恼怒', '盘问', '揣测', '忽视', '发声明', '消息来源', '臣子', '粗鲁', '中伤', '直言不讳', '强烈要求', '戏谑', '没', '举动', '捏造', '告诉', '规劝', '天下人', '责备', '自相矛盾', '公开批评', '不想', '有违', '供词', '施加压力', '疑点', '一事', '斥责', '揶揄', '在我看来', '造谣', '写道', '讯问', '无权', '诬蔑', '起身', '愚蠢', '确有', '地说', '不负责任', '歪曲', '责难', '岂', '和平解决', '难过', '子虚乌有', '确信', '无罪释放', '提到', '出庭作证', '我能', '调侃', '刻薄', '招供', '开玩笑', '强烈抗议', '论者', '谈判', '和谈', '援引', '气愤', '路透社', '拒绝', '得知', '过分', '审讯', '谬论', '时说', '口供', '自嘲', '无疑', '他称', '夸大', '没错', '不耐烦', '痛斥', '反讽', '令人兴奋', '美联社', '媒体报道', '难以置信', '犹豫', '电邮', '作答', '取笑', '反对者', '唿吁', '拒绝接受', '新闻媒体', '毫无意义', '无耻', '流泪', '怒斥', '无论如何', '称有', '显而易见', '直斥', '并非如此', '劝说', '媒体', '事实上', '同意', '编造', '可耻', '可不是', '劝谏', '讲', '谎称', '承认', '讥讽', '谏言', '从来不', '我来', '自辩']
'''
