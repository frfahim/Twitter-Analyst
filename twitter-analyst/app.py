from flask import Flask, render_template
import sqlite3
import ast

db = "tweet-data.db"

app = Flask(__name__)


@app.route("/")
def main():
    lang_data = []
    top_lang_data = []
    country_data = []
    love_words = []
    love_words_guage = []
    lang, top_lang, country, lv_words, sw_words, datetime_twt = get_lang()
    #lang, top_lang, lv_words, sw_words, datetime_twt = get_lang()

    for l in lang:
        # 1st--language, 2nd--percentage used, 3rd--same thing repeated
        lang_data.append([l[0], l[1], l[1]])
        # print(l[0], l[1], l[1])
    for tl in top_lang:
        top_lang_data.append([tl[0], tl[1], tl[1]])

    country_data.append(['Country', 'Popularity'])

    for ct in country:
        country_data.append([ct[0], ct[1]])

    love_words.append(['love_words', lv_words, lv_words])
    love_words.append(['swear_words', sw_words, sw_words])

    lw_percents = int((lv_words * 100) / (lv_words + sw_words))
    sw_percents = int((sw_words * 100) / (lv_words + sw_words))

    love_words_guage.append(['Labels', 'Value'])
    love_words_guage.append(['love_words', lw_percents])
    love_words_guage.append(['swear_words', sw_percents])

    return render_template("analyser.html", lang_data=lang_data, top_lang_data=top_lang_data,
                           country_data=country_data, love_words=love_words,
                           love_words_guage=love_words_guage, datetime_twt=datetime_twt)


def get_lang():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cn = conn.cursor()

    # Get languages
    cn.execute("SELECT * FROM lang_data ORDER BY datetime DESC")
    # cn.execute("SELECT * FROM lang_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    lang = ast.literal_eval(result['language'])
    top_lang = ast.literal_eval(result['top_lang'])

    # Get country
    cn.execute("SELECT * from country_data ORDER BY datetime DESC")
    result = cn.fetchone()
    country = ast.literal_eval(result['country'])

    # Get love & swear words
    cn.execute("SELECT * from love_data ORDER BY datetime DESC LIMIT 1")
    result = cn.fetchone()
    love_words = result['love_words']
    swear_words = result['swear_words']

    datetime_twt = result['datetime']

    conn.close()

    return lang, top_lang, country, love_words, swear_words, datetime_twt
    #return lang, top_lang, love_words, swear_words, datetime_twt


@app.route("/top_tweets")
def top_tweets():
    tweets, datetime_top_tweets = get_top_tweet()
    # datetime_top_tweets is only for debug, just so that we can check the script is running regularly
    return render_template("top_tweets.html", tweets=tweets, datetime_top_tweets=datetime_top_tweets)


def get_top_tweet():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cn = conn.cursor()
    cn.execute("SELECT * FROM twt_data ORDER BY datetime DESC LIMIT 30")  # Get last 30 tweets

    result = cn.fetchall()
    tweets = []
    datetime_top_tweets = result[0]['datetime']

    for tweet in result:
        tweets.append(tweet['top_tweet'])

    conn.close()
    return tweets, datetime_top_tweets


@app.route("/trends")
def trends():
    trend, trend_tweets, datetime_trends = get_trends()
    return render_template("trends.html", trend=trend, trend_tweets=trend_tweets, datetime_trends=datetime_trends)


def get_trends():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cn = conn.cursor()
    cn.execute("SELECT * FROM trend_data ORDER BY datetime DESC LIMIT 10")  # return top 10 trends

    trend = []
    trend_tweets = []

    result = cn.fetchall()
    datetime_trends = result[0]['datetime']

    for tt in result:
        trend.append(tt['trend'])
        trend_tweets.append(tt['trend_id1'])
        trend_tweets.append(tt['trend_id2'])
        trend_tweets.append(tt['trend_id3'])

    conn.close()
    return trend, trend_tweets, datetime_trends

if __name__ == "__main__":
    app.run(debug=True)
