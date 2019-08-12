import jieba
import json

from model.predicate import get_Synonyms_of_speak
from model.news_person import get_real_person
from model.speech import get_related_speech
Synonyms_of_speak = set(get_Synonyms_of_speak(200))


def segment_3_parts(sentence):
    """
    以谓语为中心，把句子切分成主谓宾 三部分。
    """
    words = jieba.lcut(sentence)
    print(words)
    position = predicate = None
    for i,w in enumerate(words):
        if w in Synonyms_of_speak:
            position, predicate = i, w
            break
    if position is None:
        resp = {"action": "没有发现言论"}
    else:
        before_predi = ''.join(words[:position])
        after_predi = ''.join(words[position+1:])
        person = get_real_person(before_predi)
        speech = get_related_speech(after_predi)
        resp = {
            'person': person,
            'action': predicate,
            'speech': speech
        }
    return resp
    #

    


    

