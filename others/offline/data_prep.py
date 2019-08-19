# -*- coding: utf-8 -*
#import sys
import pandas as pd
from io import open
import re
import jieba
from hanziconv import HanziConv
import os
from utils.load_data import load_stopwords
from config import DEFAULT_STOPWORDS_PATH, WIKI_DATA_PATH, NEWS_DATA_PATH, PROCESSED_DATA_PATH
STOPWORDS = load_stopwords()

def get_train_data_from_news(data_path, save_to_file):
    """
    从新闻语料库下载的csv文档里拿数据
    """
    sentences_by_word = ''
    if os.path.exists(data_path):
        print('Read data from ', data_path)
        news = pd.read_csv(data_path, error_bad_lines=False)
        news.columns = ['index', 'author', 'pulisher', 'content', 'code', 'title', 'url']
        content = news.iloc[:,3]
        for sentence in content:
            sentence = token(str(sentence))
            if sentence == '': continue
            words = jieba.cut(HanziConv.toSimplified(sentence))
            sentences_by_word = str(sentences_by_word) + ' ' + ' '.join(word for word in words if word not in STOPWORDS)
        with open(save_to_file, 'w', encoding = 'utf-8') as f:
            f.write(str(sentences_by_word) + '\n')
    else:
        print(data_path, ' does not exit')
    return sentences_by_word

def cut(string): 
    """
    分词
    """
    return ' '.join(jieba.cut(string))

def token(string): 
    """
    去除句子中的标点符号和英文
    """
    return ''.join(re.findall(r'\w+', string))

def get_path(root_path):
    """
    找到文件夹下所有的文件路径
    """
    path = []
    for folder1 in os.listdir(root_path):
        if folder1 == '.DS_Store': continue
        for folder2 in os.listdir(root_path + folder1 + '/'):
            if folder2 == '.DS_Store': continue
            path.append(root_path + folder1 + '/' + folder2)
    return path

def get_train_data_from_wiki(path, save_to_file):
    """
    从维基百科中拿数据并进行预处理
    """
    sentences_by_word = ''
    with open(path, 'r', encoding = 'utf-8') as f:
        corpus = f.readlines()
        print('Now processing:' + path)
        for sentence in corpus:
            sentence = token(str(sentence))
            if sentence == '': continue
            words = jieba.cut(HanziConv.toSimplified(sentence))
            sentences_by_word = str(sentences_by_word) + ' ' + ' '.join(word for word in words if word not in STOPWORDS)
    with open(save_to_file, 'w', encoding = 'utf-8') as f:
        f.write(str(sentences_by_word))


get_train_data_from_news(data_path = '../../'+ NEWS_DATA_PATH, save_to_file = '../../' + PROCESSED_DATA_PATH + 'processed_news.txt')
print('finish extracting train data from news')
 
paths = get_path(root_path = '../../' + WIKI_DATA_PATH)
for path in paths:
    new_path = '../../' + PROCESSED_DATA_PATH + path[-10:len(path)].replace('/','_')
    get_train_data_from_wiki(path, save_to_file = new_path)
print('finish extracting train data from wiki dump')
