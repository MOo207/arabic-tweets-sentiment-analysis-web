import datetime as dt
from snscrape.modules.twitter import TwitterSearchScraper
import pandas as pd

"""

Twitter query syntax documented here: https://github.com/igorbrigadir/twitter-advanced-search

Tweets are returned as snscrape.modules.twitter.Tweet objects.
Tweet objects are structs with the following fields:
    -url (str)
    -date (dt.datetime)
    -content (str)
    -renderedContent (str)
    -id (int)
    -user (snscrape.modules.twitter.User)
    -replyCount (int)
    -retweetCount (int)
    -likeCount (int)
    -quoteCount (int)
    -conversationId (int)
    -hashtags (list[str])
    -lang (str)
    -source (str)
    -sourceUrl (str)
    -sourceLabel (str)
    -media (list[snscrape.modules.twitter.Media])
"""


def get_tweets(query, since_time, until_time, limit=100):
    """
    query (str): a query as documented here https://github.com/igorbrigadir/twitter-advanced-search
    since_time (datetime): earliest time tweets matching query will be returned 
    until_time (datetime): latest time tweets matching query will be returned 
    limit (int): max number of tweets that will be returned 
    """
    since_time, until_time = int(since_time.timestamp()), int(until_time.timestamp())
    full_query = f'since_time:{since_time} until_time:{until_time} {query}'
    tweets = TwitterSearchScraper(full_query).get_items() 
    for count, tweet in enumerate(tweets, 1):
        yield tweet
        if count == limit:
            break

            
def get_tweet(tweet_id):
    """tweet_id (str): snowflake id of a tweet - 64 bit int"""
    since_id = int(tweet_id) - 1
    full_query = f'since_id:{since_id} max_id:{tweet_id}'
    tweet = list(TwitterSearchScraper(full_query).get_items())[0]
    return tweet


def scrape(lang,search_word):
    try:
        """Example of finding english language tweets without images
        including the text 'soccer' in the content or the username of a tweet"""
        query = 'lang:'+lang+' '+search_word
        tweets = get_tweets(query, dt.datetime(2022,4,19,0), dt.datetime(2022,5,19,1))
        reslut = []
        for tweet in tweets:
            reslut.append(tweet)
        return reslut
    except Exception as e:
        return e
