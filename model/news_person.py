"""
这个文件用来处理处理主语。
"""
from jieba import posseg

def get_real_person(long_subject):
    """
    去掉长主语的修饰词。获取真正的新闻人物实体
    :param long_subject: 原始主语。
    :return:
    """
    words = posseg.cut(long_subject)
    for w in words:
        print(w)
        if w.flag == 'nr':
            return w.word

    return long_subject
