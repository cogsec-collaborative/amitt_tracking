from snowflake import *
import pandas as pd
import json
import time
import math
import matplotlib.pyplot as plt

def get_timestamp(snowflake_id):
    timestamp, data_center, worker, sequence = melt(int(snowflake_id))
    # print('the tweet was created at {}'.format(local_datetime(timestamp)))
    return timestamp

def plot_datetimes(df, plottitle=''):
    xx = df['ymdh'].astype(str).value_counts().sort_index().reset_index()

    # Never have more than 20 labels. 
    spacing = math.ceil(len(xx)/20)
    labels = ['']*len(xx)
    for i in range(math.ceil(len(xx)/spacing)):
        labels[spacing*i] = xx['index'][spacing*i]

    plt.figure(figsize=(10,4))
    plot = plt.bar(xx['index'], xx['ymdh'], tick_label=labels)
    plt.xticks(rotation=270)
    plt.title(plottitle)
    return

def plot_hours(df, plottitle=''):
    plt.figure(figsize=(8,2))
    gps = df.groupby(['hour'])['text'].count().reset_index()
    plt.bar(gps['hour'], gps['text'])
    plt.title(plottitle)
    return


class Aptwitterlook:
    ''' Companion class to Aptwitterpull. This one analyses the results from that one... 
    '''

    def __init__(self, data_dir=''):
        # datadir contains subdirectories, one for each search in this group
        self.data_dir = data_dir


    # Helper functions for reading json, csv and formatted txt files
    def read_json(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
              return json.loads(f.read())

    def read_csv(self, filename):
        return pd.read_csv(filename)

    def read_text(self, filename):
        with open(filename, "r", encoding="utf-8") as handle:
              return handle.read()


    def read_tweets(self, searchdir):

        # Get dataset
        tweetjson = self.read_json('{}/tweets.json'.format(searchdir))
        print('We have {} tweets'.format(len(tweetjson)))
        dftweets = pd.DataFrame(tweetjson, index=[0]).transpose().reset_index()
        dftweets.rename(index=str, columns={'index': 'tweet_url', 0: 'text'}, inplace=True)
        dftweets['user'] = dftweets['tweet_url'].str.split('/').str[3]
        dftweets['tweet_id'] = dftweets['tweet_url'].str.split('/').str[5]
        dftweets['timestamp'] = dftweets['tweet_id'].apply(get_timestamp)
        dftweets['datetime'] = pd.to_datetime(dftweets['timestamp'],unit='ms')
        dftweets['date'] = dftweets['datetime'].dt.date
        dftweets['hour'] = dftweets['datetime'].dt.hour
        dftweets['ymdh'] = dftweets['datetime'].dt.year*1000000 + dftweets['datetime'].dt.month*10000 + dftweets['datetime'].dt.day*100 +dftweets['datetime'].dt.hour

        plot_datetimes(dftweets)
        
        return dftweets

    
    def hunt_bots(self, dftweets):
        
        usercounts = dftweets['user'].value_counts().reset_index()
        print('potential bots: \n{}'.format(usercounts[usercounts['user'] >= 72]))

        plot_hours(df, 'all tweets')
        for user in usercounts[usercounts['user'] >= 72]['index'].to_list():
            plot_hours(df[df['user'] == user], user)
        return usercounts

    
    def hunt_text(self, dftweets):
        return
    
    
    def analyse_targets(self, target_list):
        return
