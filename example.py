import twitter_api 
import matplotlib.pyplot as plt #for plotting data
from datetime import *
from pandas import * #for dataframe
import json #for manipulating and pretty-printing API responses
from credentials import *#credentials.py should define consumer_secret and consumer_key
#-----------------------------------

twitter = twitter_api.Twitter(consumer_key,consumer_secret)


results = twitter.search('omglol')
print json.dumps(results,indent=2)

#Follow somebody
#followed = tweet.follow_user()
#print followed

#Display who the user specified by screen_name or user_id is following
#if you do not specify a screen_name or user_id, this seems to use the 
#currently authenticated user instead
my_friends = twitter.list_friends(screen_name='enter_desired_screen_name')
print json.dumps(my_friends,indent=2)
