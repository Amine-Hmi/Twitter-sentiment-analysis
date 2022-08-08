import tweepy
import config
import re
import pandas as pd
import database as DB
import csv # to read and write csv files
import matplotlib.pyplot as plt
#import numpy as np
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
pd.set_option("display.max_rows", 15)
pd.set_option("display.max_columns", 15)
pd.set_option('display.max_colwidth', 40)


# authentication
auth = tweepy.OAuthHandler(config.API_KEY, config.API_SECRET)
auth.set_access_token(config.API_ACCESS_TOKEN, config.API_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#tweets mining
noOfTweet = int(input("Please enter how many tweets to analyze:"))
#search for english tweets containing "chris rock" AND "will smith"
keyword = '("ban" "will smith") #Oscars2022 lang:en -filter:media -filter:retweets '
#keyword = '("robert pattinson" "batman") lang:en -is:retweet'
tweet_list = [tweets for tweets in tweepy.Cursor(api.search_tweets, q=keyword,tweet_mode='extended',result_type='mixed', include_entities='false').items(noOfTweet)]

# create DataFrame
columns = ['User', 'Tweet','Score']
data = []
analyser = SentimentIntensityAnalyzer()
#calculate tweet score
def scoreCalc(text):
    score = analyser.polarity_scores(text)
    if score['compound'] >= 0.05 :
        return("Positive")

    elif score['compound'] <= - 0.05 :
        return("Negative")
 
    else :
        return("Neutral")

#remove hashtags, links and mentions from tweets
def cleanTweet(tweet):
    #remove hashtags
    hashtag_pattern = re.compile("#[A-Za-z0-9_-]*", flags=re.UNICODE)
    links_pattern = re.compile("https:\/\/.+", flags=re.UNICODE)
    mention_pattern = re.compile("@[A-Za-z0-9_-]*", flags=re.UNICODE)
    #space_pattern = re.compile("^\s+", flags=re.UNICODE)
    space_pattern = re.compile("\n", flags=re.UNICODE)
    tweet = hashtag_pattern.sub(r'', tweet)
    tweet = links_pattern.sub(r'', tweet)
    tweet = mention_pattern.sub(r'', tweet)
    tweet = space_pattern.sub(r'', tweet)
    return tweet

open('tweets.csv', 'w').close()

#initialize database
DB.db_init()

for tweet in tweet_list[::-1]:
    dump = json.dumps(tweet._json) 
    print(dump, '--\n\n--')
    tweet_id = tweet.id # get Tweet ID result
    created_at = tweet.created_at # get time tweet was created
    try:
        text = tweet.retweeted_status.full_text
    except AttributeError:  # Not a Retweet
        text = tweet.full_text
    user_screen_name = tweet.user.screen_name # retrieve user screenname
    score = scoreCalc(text)
    cleantweet = cleanTweet(text)
    text_neg= analyser.polarity_scores(text).get('neg')
    text_neu= analyser.polarity_scores(text).get('neu')
    text_pos=analyser.polarity_scores(text).get('pos')
    text_com= analyser.polarity_scores(text).get('compound')
    #text = tweet.full_text # retrieve full tweet text
   # retweet = True if(tweet.retweeted_status.full_text) else False
    data.append([tweet.user.screen_name, cleantweet ,score])
    #insert individual tweet
    DB.client['tweets_db']["tweets_collection"].insert_one({
            "_id" : tweet_id,
            "created_at" : created_at,
            "user_screen_name" : user_screen_name,
            "text" : cleantweet,
            "text_neg" : text_neg,
            "text_neu" : text_neu,
            "text_pos" : text_pos,
            "text_com" : text_com,
            "score" : score
    })

    with open('tweets.csv','a', newline='', encoding='utf-8') as csvFile:
        csv_writer = csv.writer(csvFile, delimiter=',') # create an instance of csv object
        csvFile.seek(0)
        csv_writer.writerow([tweet_id, created_at, "@"+user_screen_name, cleantweet,text_neg, text_neu, text_pos, text_com, score]) # write each row
        csvFile.truncate()


df = pd.DataFrame(data, columns=columns)
print(df)

#aggrergate tweets by percentage

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

tweets_percent = DB.client['tweets_db']["tweets_collection"].aggregate([
    {
        '$group': {
            '_id': '$_id', 
            'score': {
                '$first': '$score'
            }
        }
    }, {
        '$facet': {
            'nDocs': [
                {
                    '$count': 'nDocs'
                }
            ], 
            'groupValues': [
                {
                    '$group': {
                        '_id': '$score', 
                        'total': {
                            '$sum': 1
                        }
                    }
                }
            ]
        }
    }, {
        '$addFields': {
            'nDocs': {
                '$arrayElemAt': [
                    '$nDocs', 0
                ]
            }
        }
    }, {
        '$unwind': '$groupValues'
    }, {
        '$project': {
            '_id': 0, 
            'score': '$groupValues._id', 
            'total': '$groupValues.total', 
            'percentage': {
                '$multiply': [
                    {
                        '$divide': [
                            '$groupValues.total', '$nDocs.nDocs'
                        ]
                    }, 100
                ]
            }
        }
    }
])

percentage = []
polarity = []
for tweet in tweets_percent:
    print(tweet)
    percentage.append(tweet['percentage'])
    polarity.append(tweet['score'])

# Pie chart Colors
pie_colors = ['#2CA02C','#D62728','#FF7F0E']

# Pie chart Plot
plt.pie(percentage, labels=polarity, autopct='%.1f%%', shadow=True, colors=pie_colors)

# Pie chart Title fontsize
plt.title('Will Smith 10 years academy ban',fontsize=20)

# Display pie chart
plt.show() 
