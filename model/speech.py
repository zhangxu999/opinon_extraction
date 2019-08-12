"""
处理人物言论相关。
"""


def get_related_speech(long_sentence):
    """
    合理断句。
    :param long_sentence:
    :return:
    """
    sentences = long_sentence.replace('，', '。').split('。')
    return sentences[0]
