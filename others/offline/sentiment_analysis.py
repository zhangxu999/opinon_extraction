# -*- coding: utf-8 -*-
from snownlp import SnowNLP
from pyltp import SentenceSplitter
import pandas as pd

def split_sentences(string): # 分句
    sen = SentenceSplitter.split(string)
    sentences = [s for s in sen if len(s) != 0]
    return sentences

def get_sentence_sentiment(sentence):
    sentence_sentiment = SnowNLP(sentence).sentiments
    return sentence_sentiment

def get_news_sentiment(paragraph):
    count = 0
    total_score = 0
    para_list = split_sentences(paragraph)
    for sentence in para_list:
        sentence_sentiment = get_sentence_sentiment(sentence)
        total_score += sentence_sentiment
        count += 1
    
    return total_score / count
    

# Read news from csv file
news = pd.read_csv("news_chinese.csv", error_bad_lines = False)
news.columns = ['index', 'author', 'publisher', 'content', 'code', 'title', 'url']
news['sentiment'] = ''
news['sentiment_polarity'] = ''

# Append news sentiment to the dataframe
for i in range(len(news)):
    if news['sentiment'].iloc[i] == '':
        news_sentiment = get_news_sentiment(str(news['content'].iloc[i]))
        print(i, news_sentiment)
        news['sentiment'].iloc[i] = news_sentiment
    else:
        pass

# Assign senitment polarity to each news
for i in range(len(news)):
    if news['sentiment'].iloc[i] <= 0.3:
        news['sentiment_polarity'].iloc[i] = '负面'
    elif news['sentiment'].iloc[i] > 0.3 and news['sentiment'].iloc[i] < 0.7:
        news['sentiment_polarity'].iloc[i] = '中立'
    else:
        news['sentiment_polarity'].iloc[i] = '正面'
        
print(news['sentiment_polarity'].value_counts())
#*** Result ***
#中立    40875
#正面    39808
#负面     8924
