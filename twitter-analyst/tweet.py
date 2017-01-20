#!/usr/bin/env python3

import tweepy
from local_config import *
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
from collections import Counter
import sqlite3
import time
# regular expression
import re
# import pbd

#Country name with their languages
langs = {
    'ar': 'Arabic', 'bg': 'Bulgarian',
    'bn': 'Bengali', 'ca': 'Catalan',
    'cs': 'Czech', 'da': 'Danish',
    'de': 'German', 'el': 'Greek',
    'en': 'English', 'es': 'Spanish',
    'fa': 'Persian', 'fi': 'Finnish',
    'fr': 'French', 'hi': 'Hindi',
    'hr': 'Croatian', 'hu': 'Hungarian',
    'id': 'Indonesian', 'is': 'Icelandic',
    'it': 'Italian', 'iw': 'Hebrew',
    'ja': 'Japanese', 'ko': 'Korean',
    'lt': 'Lithuanian', 'lv': 'Latvian',
    'ms': 'Malay', 'nl': 'Dutch',
    'no': 'Norwegian', 'pl': 'Polish',
    'pt': 'Portuguese', 'ro': 'Romanian',
    'ru': 'Russian', 'sk': 'Slovak',
    'sl': 'Slovenian', 'sr': 'Serbian',
    'sv': 'Swedish', 'th': 'Thai',
    'tl': 'Filipino', 'tr': 'Turkish',
    'uk': 'Ukrainian', 'ur': 'Urdu',
    'vi': 'Vietnamese', 'et': 'Estonian',
    'zh_CN': 'Chinese(simplified)', 'zh_TW': 'Chinese (traditional)'
}

# List of countries
countries_list = ['Algeria', 'Argentina', 'Bangladesh', 'Benin', 'Botswana', 'Brazil', 'Cameroon',
                  'Central African Republic', 'Chad', 'Comoros', 'Congo', 'Egypt', 'Equatorial Guinea', 'Eritrea',
                  'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia',
                  'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Morocco', 'Niger', 'Nigeria', 'Senegal',
                  'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Switzerland', 'Sweden', 'Tanzania', 'Tunisia',
                  'Uganda', 'Zambia', 'Zimbabwe', 'Afghanistan', 'Bahrain', 'Bhutan', 'Brunei', 'Burma (Myanmar)',
                  'Cambodia', 'China', 'East Timor', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan',
                  'Kazakhstan', 'Korea', 'Korea', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives',
                  'Mongolia', 'Nepal', 'Oman', 'Pakistan', 'Philippines', 'Qatar', 'Russian Federation', 'Saudi Arabia',
                  'Singapore', 'Sri Lanka', 'Syria', 'Tajikistan', 'Thailand', 'Turkey', 'Turkmenistan',
                  'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen', 'Albania', 'Andorra', 'Armenia', 'Austria',
                  'Azerbaijan', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus',
                  'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Georgia', 'Germany', 'Greece',
                  'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg',
                  'Macedonia', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'Norway', 'Poland',
                  'Portugal', 'Romania', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Ukraine',
                  'United Kingdom', 'Vatican City', 'Antigua and Barbuda', 'Bahamas', 'Barbados', 'Belize', 'Canada',
                  'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic', 'El Salvador', 'Grenada', 'Guatemala',
                  'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Saint Kitts and Nevis',
                  'Saint Lucia', 'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'United States',
                  'Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'New Zealand', 'Palau',
                  'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu', 'Argentina', 'Bolivia',
                  'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay',
                  ]

swear_words = ["bastard", "fuck", "shit", "bitch", "idiot"]
love_words = ["love", "thank", "happy", "bless"]

programing_lang_list = ["Java", "JavaScript", "PHP", "Python", "Ruby"]

# Database file name
db = "tweet-data.db"


class TwtUtils():
    def __init__(self, api):
        self.api = api

    def get_tweet_html(self, id):
        oembed = self.api.get_oembed(id=id, hide_media=True, hide_thread=True)
        twt_html = oembed['html'].strip('\n')
        return twt_html


class Stats():
    def __init__(self):
        self.lang = []
        self.top_lang = []
        self.top_tweets = []
        self.countries = []
        self.tweets_grab = 0
        self.love_words = 0
        self.swear_words = 0
        self.programing_lang = []

    def add_lang(self, lang):
        self.lang.append(lang)

    def add_top_lang(self, top_lang):
        self.top_lang.append(top_lang)

    def add_top_tweets(self, tweet_html):
        self.top_tweets.append(tweet_html)

    def add_countries(self, country):
        self.countries.append(country)

    def set_tweets_grab(self):
        self.tweets_grab += 1

    def get_tweets_grab(self):
        return self.tweets_grab

    def found_love_words(self):
        self.love_words += 1

    def found_swear_words(self):
        self.swear_words += 1

    def add_programing_lang(self, pro_lang):
        self.programing_lang.append(pro_lang)

    def get_stats(self):
        return self.lang, self.top_lang, self.top_tweets, self.countries, self.love_words, self.swear_words,\
               self.programing_lang


# Twitter Stream Listener Class


class TwitterListener(StreamListener):
    def __init__(self, num_tweets_to_grab, stats, twt_utils, retweet_count):
        self.counter = 0
        self.num_tweets_to_grab = num_tweets_to_grab
        self.stats = stats
        self.twt_utils = twt_utils
        self.retweet_count = retweet_count
        self.tweets_grab = 0

    def on_data(self, data):
        try:
            json_data = json.loads(data)
            self.stats.add_lang(langs[json_data['lang']])
            retweet_count = json_data['retweeted_status']['retweet_count']

            if retweet_count >= self.retweet_count:
                self.stats.add_top_lang(langs[json_data['lang']])
                twt_html = self.twt_utils.get_tweet_html(json_data['id'])
                self.stats.add_top_tweets(twt_html)

            self.stats.set_tweets_grab()

            tweet = json_data['text']

            for country in countries_list:
                country_local = "\\b" + country + "\\b"
                if re.findall(country_local, tweet, flags=re.IGNORECASE):
                    self.stats.add_countries(country)

            # This is for USA & UK, since no one uses its full name on Twitter

            if re.findall("\\busa\\b", tweet, flags=re.IGNORECASE):
                self.stats.add_countries("United States")

            if re.findall("\\bbritain\\b", tweet, flags=re.IGNORECASE):
                    self.stats.add_countries("United Kingdom")

            for lw in love_words:
                if lw in tweet.lower():
                    self.stats.found_love_words()

            for lw in swear_words:
                if lw in tweet.lower():
                    self.stats.found_swear_words()

            for pro_lang in programing_lang_list:
                pro_lang_local = "\\b" + pro_lang + "\\b"
                if re.findall(pro_lang_local, tweet, flags=re.IGNORECASE):
                    self.stats.add_programing_lang(pro_lang)

            self.counter += 1
            if self.counter >= self.num_tweets_to_grab:
                return False

            return True

        except:
            # pdb.set_trace()
            pass

    def on_error(self, status):
        print("There is a Error!")
        print(status)


#Main function, all main works here
class TwitterMain():
    def __init__(self, num_tweets_to_grab, retweet_count, conn):
        self.auth = tweepy.OAuthHandler(cons_tok, cons_sec)
        self.auth.set_access_token(app_tok, app_sec)

        self.api = tweepy.API(self.auth)
        self.twt_utils = TwtUtils(self.api)

        self.stats = Stats()

        self.conn = conn
        self.c = self.conn.cursor()

        self.num_tweets_to_grab = num_tweets_to_grab
        self.retweet_count = retweet_count
	
	#Stremning data
    def get_streaming_data(self):
        twts_grabbed = 0
        while twts_grabbed < self.num_tweets_to_grab:

            twitter_stream = Stream(self.auth, TwitterListener(self.num_tweets_to_grab, self.stats,
                                                               self.twt_utils, self.retweet_count))
            # twitterStream.filter(track=["bangladesh"])
            try:
                twitter_stream.sample()
            except Exception as e:
                print("Error. Restarting Stream...")
                print(e.__doc__)
                time.sleep(3)  # Sleep for 5 minutes if error occurred
            finally:
                twts_grabbed = self.stats.get_tweets_grab()
                print("Tweets Grabbed = ", twts_grabbed)

        lang, top_lang, top_tweets, countries, lv_words, sw_words, pro_lang = self.stats.get_stats()

        '''
        print(Counter(lang))
        print(Counter(top_lang))
        print("Love Words {} Swear Words {}".format(love_words, swear_words))
        '''

        print("Is it working?...")
        self.c.execute("INSERT INTO lang_data VALUES (?,?, DATETIME('now'))",
                       (str(list(Counter(lang).items())), str(list(Counter(top_lang).items()))))

        for tt in top_tweets:
            self.c.execute("INSERT INTO twt_data VALUES (?, DATETIME('now'))", (tt,))

        self.c.execute("INSERT INTO love_data VALUES (?,?, DATETIME('now'))", (lv_words, sw_words))
        print("Till now ok?  then....")
        data = str(list(Counter(countries).items()))
        print(data)
        self.c.execute("INSERT INTO country_data VALUES (?, DATETIME('now'))", (data,))

        pl_data = str(list(Counter(pro_lang).items()))
        print(pl_data)
        self.c.execute("INSERT INTO pro_lang_data VALUES (?, DATETIME('now'))", (pl_data,))

        self.conn.commit()
        print("Yes it works!")

    # end streaming

    # Grab trends from twitter
    def get_trends(self):
        trends = self.api.trends_place(1)
        trend_data = []

        for trend in trends[0]["trends"]:
            trend_tweets = []
            #print trend['name']
            trend_tweets.append(trend['name'])

            search_results = tweepy.Cursor(self.api.search, q=trend['name']).items(3)
            for result in search_results:
                twt_html = self.twt_utils.get_tweet_html(result.id)
                trend_tweets.append(twt_html)
                # print twt_html

            trend_data.append(tuple(trend_tweets))

        # self.c.executemany("INSERT INTO trend_data VALUES (?,?,?,?, DATETIME('now'))", (trend_data))
        self.c.executemany("INSERT INTO trend_data VALUES (?, ?, ?, ?, DATETIME('now'))", trend_data)
        self.conn.commit()

    # End trends


if __name__ == "__main__":
    num_tweets_to_grab = 50000
    retweet_count = 10000
    try:
        conn = sqlite3.connect(db)
        twt = TwitterMain(num_tweets_to_grab, retweet_count, conn)
        twt.get_streaming_data()
        twt.get_trends()

    except Exception as e:
        print(e.__doc__)

    finally:
        conn.close()
