# pip install snscrape
# pip install streamlit
# pip install pymongo

import datetime
import snscrape.modules.twitter as sntwitter
import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
from PIL import Image #Python Imaging Library
from datetime import date
import json

# Mongodb client connection is done
client = MongoClient("mongodb://localhost:27017/")
db = client.twitter_Scrape
record = db.Scrapped_data


st.title('_:green[Twitter Scraper]_')


#Creating the empty list to add the data
twt_list = []

# Menus used in Twitter Scrape web app -- 3 menus are used
choice = st.sidebar.selectbox('Menu',["Search","Display","Download"])


#Menu "search"
if choice=="Search":

    # First we need to clear the previous scaraped tweets
    clear = record.delete_many({})

    item = st.selectbox('which you want to search ?',['Hashtag','Username'])
    st.write('you have selected', item)
    items = ['Hashtag','Username']

    #getting dates from user
    d1 = st.date_input('Enter the start date:',datetime.date(2023, 1, 1))
    st.write('Tweets starts from', d1)

    d2 = st.date_input('Enter the end date:',datetime.date(2023, 4, 7))
    st.write('Tweets ended at', d2)

    #Getting text to search from user and scrap the tweets using snscrap
    if item in items:
        search_text = st.text_input('Enter the text:')
        date_range = ' since:'+d1.strftime("%Y-%m-%d")+' until:'+d2.strftime("%Y-%m-%d")
        query= search_text+date_range
        number = st.number_input('Enter the number of tweets you wanted to scrape',1,1000)
        st.write(query)

       # collecting all the data using the sncrape i.e. sntwitter
        scraper = sntwitter.TwitterSearchScraper(query)
        st.write(scraper)
        for i, tweet in enumerate(scraper.get_items()):
            if i >1000:
                break
            twt_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username, tweet.replyCount, tweet.retweetCount, tweet.lang, tweet.source, tweet.likeCount, tweet.url])

        #Here we converted data into dataframe using pandas
        df1 = pd.DataFrame(twt_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username', 'Reply Count', 'Retweet_Count','Language', 'Source', 'Like_Count', 'URL'])

        #storing dataframe into mongodb with json
        tweet_data = json.loads(df1.to_json(orient='records'))
        record.insert_many(list(tweet_data))
        st.write('Tweets successfully scraped')

#menu 'Display'
elif choice=="Display":
    # Save the documents in a dataframe
    df2 = pd.DataFrame(list(record.find()))
    #Dispaly the document
    st.dataframe(df2)

# Menu 3 is for Downloading the scraped data as CSV or JSON
else:
   col1, col2 = st.columns(2)

   # Download the scraped data as CSV
   with col1:
       st.write("Download the tweet data as CSV File")
       # save the documents in a dataframe
       df = pd.DataFrame(list(record.find()))
       # Convert dataframe to csv
       df.to_csv('twittercsv.csv')


       def convert_df(data):
           # Cache the conversion to prevent computation on every rerun
           return df.to_csv().encode('utf-8')


       csv = convert_df(df)
       st.download_button(
           label="Download data as CSV",
           data=csv,
           file_name='twtittercsv.csv',
           mime='text/csv',
       )


   # Download the scraped data as JSON

   with col2:
       st.write("Download the tweet data as JSON File")
       # Convert dataframe to json string instead as json file
       twtjs = df.to_json(default_handler=str).encode()
       # Create Python object from JSON string data
       obj = json.loads(twtjs)
       js = json.dumps(obj, indent=4)
       st.download_button(
           label="Download data as JSON",
           data=js,
           file_name='twtjs.js',
           mime='text/js',
       )
