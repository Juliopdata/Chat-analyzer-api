import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from statistics import mean
def sentimentAnalyzer(data):
    sid = SentimentIntensityAnalyzer()
    emotions = {}
    emotions['msgs'] = {}
    
    for key, value in data.items():
        emotions['msgs'][key] = value
        emotions['msgs'][key]['sentiments'] = sid.polarity_scores(value['text'])
    
    emotions['ANALYSIS'] = {'mean_neg': mean([value['sentiments']['neg'] for value in emotions['msgs'].values()]),
                                         'MEAN_NEGATIVE': mean([value['sentiments']['neu'] for value in emotions['msgs'].values()]), 
                                         'MEAN_POSITIVE': mean([value['sentiments']['pos'] for value in emotions['msgs'].values()]), 
                                         'MEAN_TOTAL': mean([value['sentiments']['compound'] for value in emotions['msgs'].values()])}
    
    return emotions