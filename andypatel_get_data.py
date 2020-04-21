from collections import Counter
from itertools import combinations
from twarc import Twarc
import requests
import sys
import os
import shutil
import io
import re
import json

# From https://labsblog.f-secure.com/2018/02/16/searching-twitter-with-twarc/
 
# Helper functions for saving json, csv and formatted txt files
def save_json(variable, filename):
  with io.open(filename, "w", encoding="utf-8") as f:
    f.write(json.dumps(variable, indent=4, ensure_ascii=False))
 
def save_csv(data, filename):
  with io.open(filename, "w", encoding="utf-8") as handle:
    handle.write(u"Source,Target,Weight\n")
    for source, targets in sorted(data.items()):
      for target, count in sorted(targets.items()):
        if source != target and source is not None and target is not None:
          handle.write(source + u"," + target + u"," + str(count) + u"\n")
 
def save_text(data, filename):
  with io.open(filename, "w", encoding="utf-8") as handle:
    for item, count in data.most_common():
      handle.write(str(count) + "\t" + item + "\n")
 
# Returns the screen_name of the user retweeted, or None
def retweeted_user(status):
  if "retweeted_status" in status:
    orig_tweet = status["retweeted_status"]
    if "user" in orig_tweet and orig_tweet["user"] is not None:
      user = orig_tweet["user"]
      if "screen_name" in user and user["screen_name"] is not None:
        return user["screen_name"]
 
# Returns a list of screen_names that the user interacted with in this Tweet
def get_interactions(status):
  interactions = []
  if "in_reply_to_screen_name" in status:
    replied_to = status["in_reply_to_screen_name"]
    if replied_to is not None and replied_to not in interactions:
      interactions.append(replied_to)
  if "retweeted_status" in status:
    orig_tweet = status["retweeted_status"]
    if "user" in orig_tweet and orig_tweet["user"] is not None:
      user = orig_tweet["user"]
      if "screen_name" in user and user["screen_name"] is not None:
        if user["screen_name"] not in interactions:
          interactions.append(user["screen_name"])
  if "quoted_status" in status:
    orig_tweet = status["quoted_status"]
    if "user" in orig_tweet and orig_tweet["user"] is not None:
      user = orig_tweet["user"]
      if "screen_name" in user and user["screen_name"] is not None:
        if user["screen_name"] not in interactions:
          interactions.append(user["screen_name"])
  if "entities" in status:
    entities = status["entities"]
    if "user_mentions" in entities:
      for item in entities["user_mentions"]:
        if item is not None and "screen_name" in item:
          mention = item['screen_name']
          if mention is not None and mention not in interactions:
            interactions.append(mention)
  return interactions
 
# Returns a list of hashtags found in the tweet
def get_hashtags(status):
  hashtags = []
  if "entities" in status:
    entities = status["entities"]
    if "hashtags" in entities:
      for item in entities["hashtags"]:
        if item is not None and "text" in item:
          hashtag = item['text']
          if hashtag is not None and hashtag not in hashtags:
            hashtags.append(hashtag)
  return hashtags
 
# Returns a list of URLs found in the Tweet
def get_urls(status):
  urls = []
  if "entities" in status:
    entities = status["entities"]
    if "urls" in entities:
      for item in entities["urls"]:
        if item is not None and "expanded_url" in item:
          url = item['expanded_url']
          if url is not None and url not in urls:
            urls.append(url)
  return urls
 
# Returns the URLs to any images found in the Tweet
def get_image_urls(status):
  urls = []
  if "entities" in status:
    entities = status["entities"]
    if "media" in entities:
      for item in entities["media"]:
        if item is not None:
          if "media_url" in item:
            murl = item["media_url"]
            if murl not in urls:
              urls.append(murl)
  return urls
 
# Main starts here
if __name__ == '__main__':
# Add your own API key values here
  fsecret = open('/Users/sara/twittersecrets.txt', 'r')
  secrets = fsecret.readline()
  access_token, access_token_secret, consumer_key, consumer_secret = \
      [x.strip() for x in secrets.split(',')]
 
  twarc = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)
 
# Check that search terms were provided at the command line
  target_list = []
  if (len(sys.argv) > 1):
    target_list = sys.argv[1:]
  else:
    print("No search terms provided. Exiting.")
    sys.exit(0)
 
  num_targets = len(target_list)
  for count, target in enumerate(target_list):
    print(str(count + 1) + "/" + str(num_targets) + " searching on target: " + target)
# Create a separate save directory for each search query
# Since search queries can be a whole sentence, we'll check the length
# and simply number it if the query is overly long
    if not os.path.exists("data/twitter"):
      os.makedirs("data/twitter")
    save_dir = "data/twitter/"
    if len(target) < 30:
      save_dir += target.replace(" ", "_")
    else:
      save_dir += "target_" + str(count + 1)
    if not os.path.exists(save_dir):
      print("Creating directory: " + save_dir)
      os.makedirs(save_dir)
# Variables for capturing stuff
    tweets_captured = 0
    influencer_frequency_dist = Counter()
    mentioned_frequency_dist = Counter()
    hashtag_frequency_dist = Counter()
    url_frequency_dist = Counter()
    user_user_graph = {}
    user_hashtag_graph = {}
    hashtag_hashtag_graph = {}
    all_image_urls = []
    tweets = {}
    tweet_count = 0
# Start the search
    for status in twarc.search(target):
# Output some status as we go, so we know something is happening
      sys.stdout.write("\r")
      sys.stdout.flush()
      sys.stdout.write("Collected " + str(tweet_count) + " tweets.")
      sys.stdout.flush()
      tweet_count += 1
    
      screen_name = None
      if "user" in status:
        if "screen_name" in status["user"]:
          screen_name = status["user"]["screen_name"]
 
      retweeted = retweeted_user(status)
      if retweeted is not None:
        influencer_frequency_dist[retweeted] += 1
      else:
        influencer_frequency_dist[screen_name] += 1
 
# Tweet text can be in either "text" or "full_text" field...
      text = None
      if "full_text" in status:
        text = status["full_text"]
      elif "text" in status:
        text = status["text"]
 
      id_str = None
      if "id_str" in status:
        id_str = status["id_str"]
 
# Assemble the URL to the tweet we received...
      tweet_url = None
      if "id_str" is not None and "screen_name" is not None:
        tweet_url = "https://twitter.com/" + screen_name + "/status/" + id_str
 
# ...and capture it
      if tweet_url is not None and text is not None:
        tweets[tweet_url] = text
 
# Record mapping graph between users
      interactions = get_interactions(status)
      if interactions is not None:
        for user in interactions:
          mentioned_frequency_dist[user] += 1
          if screen_name not in user_user_graph:
            user_user_graph[screen_name] = {}
          if user not in user_user_graph[screen_name]:
            user_user_graph[screen_name][user] = 1
          else:
            user_user_graph[screen_name][user] += 1
 
# Record mapping graph between users and hashtags
      hashtags = get_hashtags(status)
      if hashtags is not None:
        if len(hashtags) > 1:
          hashtag_interactions = []
# This code creates pairs of hashtags in situations where multiple
# hashtags were found in a tweet
# This is used to create a graph of hashtag-hashtag interactions
          for comb in combinations(sorted(hashtags), 2):
            hashtag_interactions.append(comb)
          if len(hashtag_interactions) > 0:
            for inter in hashtag_interactions:
              item1, item2 = inter
              if item1 not in hashtag_hashtag_graph:
                hashtag_hashtag_graph[item1] = {}
              if item2 not in hashtag_hashtag_graph[item1]:
                hashtag_hashtag_graph[item1][item2] = 1
              else:
                hashtag_hashtag_graph[item1][item2] += 1
          for hashtag in hashtags:
            hashtag_frequency_dist[hashtag] += 1
            if screen_name not in user_hashtag_graph:
              user_hashtag_graph[screen_name] = {}
            if hashtag not in user_hashtag_graph[screen_name]:
              user_hashtag_graph[screen_name][hashtag] = 1
            else:
              user_hashtag_graph[screen_name][hashtag] += 1
 
      urls = get_urls(status)
      if urls is not None:
        for url in urls:
          url_frequency_dist[url] += 1
 
      image_urls = get_image_urls(status)
      if image_urls is not None:
        for url in image_urls:
          if url not in all_image_urls:
            all_image_urls.append(url)
 
# Iterate through image URLs, fetching each image if we haven't already
      print
      print("Fetching images.")
      pictures_dir = os.path.join(save_dir, "images")
      if not os.path.exists(pictures_dir):
        print("Creating directory: " + pictures_dir)
        os.makedirs(pictures_dir)
      for url in all_image_urls:
        m = re.search("^http:\/\/pbs\.twimg\.com\/media\/(.+)$", url)
        if m is not None:
          filename = m.group(1)
          print("Getting picture from: " + url)
          save_path = os.path.join(pictures_dir, filename)
          if not os.path.exists(save_path):
            response = requests.get(url, stream=True)
            with open(save_path, 'wb') as out_file:
              shutil.copyfileobj(response.raw, out_file)
            del response
 
# Output a bunch of files containing the data we just gathered
      print("Saving data.")
      json_outputs = {"tweets.json": tweets,
                      "urls.json": url_frequency_dist,
                      "hashtags.json": hashtag_frequency_dist,
                      "influencers.json": influencer_frequency_dist,
                      "mentioned.json": mentioned_frequency_dist,
                      "user_user_graph.json": user_user_graph,
                      "user_hashtag_graph.json": user_hashtag_graph,
                      "hashtag_hashtag_graph.json": hashtag_hashtag_graph}
      for name, dataset in json_outputs.items():
        filename = os.path.join(save_dir, name)
        save_json(dataset, filename)
 
# These files are created in a format that can be easily imported into Gephi
      csv_outputs = {"user_user_graph.csv": user_user_graph,
                     "user_hashtag_graph.csv": user_hashtag_graph,
                     "hashtag_hashtag_graph.csv": hashtag_hashtag_graph}
      for name, dataset in csv_outputs.items():
        filename = os.path.join(save_dir, name)
        save_csv(dataset, filename)
 
      text_outputs = {"hashtags.txt": hashtag_frequency_dist,
                      "influencers.txt": influencer_frequency_dist,
                      "mentioned.txt": mentioned_frequency_dist,
                      "urls.txt": url_frequency_dist}
      for name, dataset in text_outputs.items():
        filename = os.path.join(save_dir, name)
        save_text(dataset, filename)
