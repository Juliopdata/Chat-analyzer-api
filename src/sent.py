import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from statistics import mean
def sentimentAnalyzer(data):
    sid = SentimentIntensityAnalyzer()
    newdata = {}
    newdata['messages'] = {}
    for key, value in data.items():
        newdata['messages'][key] = value
        newdata['messages'][key]['sentiments'] = sid.polarity_scores(value['text'])
    newdata['chat_sentiment_analysis'] = {'mean_neg': mean([value['sentiments']['neg'] for value in newdata['messages'].values()]),
                                         'mean_neu': mean([value['sentiments']['neu'] for value in newdata['messages'].values()]), 
                                         'mean_pos': mean([value['sentiments']['pos'] for value in newdata['messages'].values()]), 
                                         'mean_compound': mean([value['sentiments']['compound'] for value in newdata['messages'].values()])}
    return newdata