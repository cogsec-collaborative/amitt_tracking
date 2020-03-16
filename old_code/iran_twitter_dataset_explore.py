#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd

df = pd.read_csv('../datasets/2018_10_twitter_election_integrity/Iran/iranian_tweets_csv_hashed.csv')
df['tweetyear'] = df['tweet_time'].str[:4]
df.head()


# In[67]:


df.dtypes


# Play with dataset a little. Questions / thoughts: 
# 
# * why does the volume dip in 2016? 
# * Languages switch over the years. 2014, French dominates; after that stabilises on English then Arabic
# * Top tweeters turn out to be impressively multilingual - wonder if we can use that as a tell? (more specifically, do they tweet in one language for a period of time then switch to another? Can we start spotting trollbots by their inconsistency over time perhaps?)
# * Question: how much meaning is in the # content?  Like, are people using #this #is #a #message, or just using the hashtags to get amplification?  How the hashtags are used is quite interesting here
# * Lots of 'news org' in the top-followed accounts. Are these real or fake? Is their output primarily message-based (e.g. for power), or url-based (e.g. for the advertising dollars)? (yes, yes, it could be both, but worth asking - URLs are a good vulnerability). 
# 
# This influence thing is interesting.  Lots of single tweets here. If you're running a network, you don't amplify your content with your other trollbots?  Is there a reason for that?  Do those non-amplified tweets get reach in a different way - perhaps by being well targetted, or being part of a set of related tweets, or being from very visible accounts? 

# In[9]:


df['tweetyear'].value_counts().sort_index()


# In[17]:


df[['userid', 'tweetyear', 'is_retweet']].pivot_table(columns='tweetyear', index='is_retweet', aggfunc='count')


# In[26]:


get_ipython().run_line_magic('matplotlib', 'inline')
dfbylang = df[['userid', 'tweetyear', 'tweet_language']].pivot_table(index='tweetyear', columns='tweet_language', aggfunc='count')
dfbylang.plot(figsize=(15,7)) #legend=False, 
dfbylang


# In[56]:


toplangs = {}
dfbylang2 = dfbylang['userid'].transpose()
for year in range(2010, 2019):
    stryr = str(year)
    try:
        toplangs[stryr] = dfbylang2[dfbylang2[stryr].notnull()].sort_values(stryr, ascending=False)[stryr][:5].to_dict()
        print('{} {}'.format(stryr, toplangs[stryr]))
    except:
        continue


# In[57]:


# Okay, who's tweeting most
df['user_screen_name'].value_counts()


# In[58]:


# What the hell is with those long screen names - language?
df[df['user_screen_name'] == 'a51115862ba4725c846e77683e9c71d1b1eb246100ca394f1b915f9c7909099d']


# In[65]:


# What languages are the top users writing in?
topusers = df['user_screen_name'].value_counts().index[:10]
dfuserbylang = df[df['user_screen_name'].isin(topusers)][['userid', 'user_screen_name', 'tweet_language']].pivot_table(columns='user_screen_name', index='tweet_language', aggfunc='count')
dfuserbylang


# In[66]:


# Do these answers change if we look at original content (e.g. non-retweets)?
dforig = df[df['is_retweet'] ==  False]
topusers2 = dforig['user_screen_name'].value_counts().index[:10]
dfuserbylang2 = dforig[dforig['user_screen_name'].isin(topusers2)][['userid', 'user_screen_name', 'tweet_language']].pivot_table(columns='user_screen_name', index='tweet_language', aggfunc='count')
dfuserbylang2


# In[68]:


df['tweet_text'].value_counts()


# In[98]:


dforig['tweet_text'].value_counts()


# In[ ]:


# Let's look at the meat in the text.  
# Strip it down to the non-repeats (keep the first of each set)
# Strip out the # and @ content
# And then look at what people are talking about


# In[94]:


str = 'RT @1fd0ed9f8d4e3966ed7ba6941d24072d6582e9aa0fda18b52635b7d0b8e03b1a: #MBCTheVoice #شي_تتميز_فيه_الكويت #الخميس_الدامي #ذكري #كتابات_منيره #عيسى_قاسم #إرادتنا_إقوى #البحرين #bahrain #المقاو… '
#str = 'RT @libertyfrontpr: #InternationalQudsDay2018   #QudsDay4Return#InternationalQudsDay2018   Stop#NAKBA70  #EuropeanQudsPlatform #BDS #Jerusa… '
wds = str.split(' ')
wds


# In[97]:


ddf = pd.DataFrame(wds)
' '.join(ddf[(ddf[0] != '') & (~ddf[0].str[0].isin(['@', '#']))][0].tolist())


# In[99]:


# Thinking about how viral things go.  How do they get their message out? 

# try this, to check that the user profile doesn't change over time in this dataset
df[df['user_screen_name'] == 'marialuis91']['follower_count'].value_counts()


# In[104]:


# So there really are only 660 accounts listed here. That was a surprise. First reaction: 
# that's either really bad bot software, or a really small team
print(len(df['user_screen_name'].unique()))
print(len(dforig['user_screen_name'].unique()))


# In[105]:


# So what the hell software are they using then?
df['tweet_client_name'].value_counts()


# In[101]:


dfusers = df.drop_duplicates(subset=['user_screen_name'], keep='last')
dfusers


# In[114]:


# What at the follower counts like, and what do accounts claim to be
dfusers.sort_values('follower_count', ascending=False)[['user_screen_name', 'follower_count', 'user_profile_description']]


# In[ ]:




