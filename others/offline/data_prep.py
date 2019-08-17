# -*- coding: utf-8 -*-
import pandas as pd
from io import open
import re
import jieba
from hanziconv import HanziConv
import os
import pickle


def get_train_data_from_news(data_path, save_to_file):
    """
    从新闻语料库下载的csv文档里拿数据
    """
    
    sentences_by_word = list()
    
    if os.path.exists(data_path):
        print('Read data from ', data_path)
        news = pd.read_csv(data_path, error_bad_lines=False)
        news.columns = ['index', 'author', 'pulisher', 'content', 'code', 'title', 'url']
        content = news.iloc[:,3]
        for sentence in content:
            sentence = token(str(sentence))
            print('finish tokenization')
            if sentence == '': continue
            words = jieba.cut(HanziConv.toSimplified(sentence))
            sentences_by_word.append([word for word in words if word not in stop_words])
        
        with open(save_to_file, 'wb') as f:
            pickle.dump(sentences_by_word, f)
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


def get_stop_words(file_path):
    """
    读取停用词列表
    """

    stop_words = []
    
    if os.path.exists(file_path):
        with open(file_path,'r', encoding = 'utf-8') as f:
            stop_words = [x.strip() for x in f.readlines()]
    else:
        print('Stop words file does not exist')
    return stop_words

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

def get_train_data_from_wiki(path, stop_words, save_to_folder):
    """
    从维基百科中拿数据并进行预处理，并保存
    """

    sentences_by_word = []
    with open(path, 'r', encoding = 'utf-8') as f:
        corpus = f.readlines()
        print('Now processing:' + path)
        for sentence in corpus:
            sentence = token(str(sentence))
            if sentence == '': continue
            words = jieba.cut(HanziConv.toSimplified(sentence))
            sentences_by_word.append([word for word in words if word not in stop_words])
    with open(save_to_folder + path[-10:len(path)], 'wb') as f:
        pickle.dump(sentences_by_word, f) # processed data is in list format

def load_train_data(train_data_path):
    """
    从指定的路径中读取数据并合并数据（处理nested folder）
    """

    train_data = list()
    for folder in os.listdir(train_data_path):
        for filename in os.listdir(train_data_path + folder + '/'):
            if filename == '.DS_Store': continue
            file_path = train_data_path + str(folder) + '/' + str(filename)
            with open(file_path, 'rb') as f:
                print(file_path)
                train_data.extend(pickle.load(f))
    return train_data

def load_train_data2(train_data_path):
    """
    从指定的路径中读取数据并合并数据（不处理nested folder）
    """
 
    train_data = list()
    for filename in os.listdir(train_data_path):
        if filename == '.DS_Store': continue
        file_path = train_data_path + str(filename)
        with open(file_path, 'rb') as f:
            print(file_path)
            train_data.extend(pickle.load(f))
    return train_data

def save_train_data_list(train_data, save_to_file):
    """
    保存完整的训练数据为list
    """

    with open(save_to_file, 'wb') as f:
        pickle.dump(train_data, f)

if __name__ == '__main__':
    
    stop_words = get_stop_words(file_path = '../database/stop_words/哈工大停用词表.txt')
    print('finish extracting stop words.')
    
    get_train_data_from_news(data_path = '../database/dataset/news_chinese.csv', save_to_file = '../../Reference/wikiextractor-master/processed_text/cutted_news/cutted_news.txt')
    print('finish extracting train data from news')
    
    paths = get_path(root_path = '../../Reference/wikiextractor-master/text/')
    
    
    for path in paths:
        get_train_data_from_wiki(path, stop_words, save_to_folder = '../../Reference/wikiextractor-master/processed_text/')

    print('finish extracting train data from wiki dump')
    
    train_data = load_train_data(train_data_path = '../../Reference/wikiextractor-master/processed_text/')
    #train_data = load_train_data2(train_data_path = '../../Reference/wikiextractor-master/processed_text/cutted_news/')
    
    print('finish loading train data')
    
    save_train_data_list(train_data, save_to_file = '../../Reference/wikiextractor-master/training_data/training_data.txt')
    
    print('finish saving training data')