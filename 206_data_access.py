###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)




######### END INSTRUCTIONS #########

# Put all import statements you need here.
import unittest
import tweepy
import json
from twitter_info import consumer_key, consumer_secret, access_token, access_token_secret #(use similar file to how we have used in previous homeworks)
import sqlite3
import os
import requests
import re
# Begin filling in instructions....
#this sets up twitter application, connects to API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser()) 

#this caches and pulls data into a .txt file
def twitter_data(search_term):
	try:
		file1= open('{}.json'.format(search_term), 'r')
		return json.loads(file1.read())
	except:
		print ("Making live request for twitter...\n\n\n\n")
		public_tweets = api.search(q=search_term)
		file2= open('{}.json'.format(search_term), 'w')
		file2.write(json.dumps(public_tweets))
		return public_tweets
# print (twitter_data("Air Bud")) #this invokes cache function

def twitter_user(user_id):
	try:
		userfile= open('user_{}.json'.format(user_id), 'r')
		return json.loads(userfile.read())
	except:
		print ('Making live request twitter user...\n\n\n\n')
		public_tweets = api.get_user(user_id)
		userfile2= open('user_{}.json'.format(user_id), 'w')
		userfile2.write(json.dumps(public_tweets))
		return public_tweets

def OMDB_data(movie_title):
	try:
		OMDBcache=open('movie_{}.json'.format(movie_title))
		return json.loads(OMDBcache.read())
	except:
		print ("Making live request from OMDB...\n\n\n\n")
		base_url= "http://www.omdbapi.com/?"
		params= {"t": movie_title}
		omdb1= requests.get(base_url, params= params).json()
		OMDBfile2= open('movie_{}.json'.format(movie_title), 'w')
		OMDBfile2.write(json.dumps(omdb1))
		return omdb1

# print (OMDB_data("Harry Potter"))

# print (twitter_data("Air Bud")['statuses'][0])

# print (twitter_user('18723984'))

class Movie ():
	def __init__(self, movie):
		self.movie_id= movie['imdbID']
		self.title= movie['Title']
		self.director=movie ['Director']
		self.rating= movie['imdbRating']
		self.actors= movie['Actors'].split(',')
		self.languages= len(movie['Language'].split(','))
		self.languagelst= movie['Language']

	def __str__(self):
		return "My favorite movie is {}".format(self.title)
	def lst_languages(self):
		return self.languagelst.split(',')

class Tweet():
	def __init__(self, tweet):
		self.tweet_text= tweet['text']
		self.tweet_id=tweet['id_str']
		self.user= tweet['user']['id_str']
		self.favorites= tweet['favorite_count']
		self.retweets= tweet['retweet_count']

	def get_user_data(self):
		user1= twitter_user(self.user)
		self.screen_name= user1['screen_name']
		self.user_favorites=user1['favourites_count']
		

Omdb_movielst= ["Air Bud", "Shrek", "Casino Royale"]

movies=[]

for each in Omdb_movielst:
	movie_tweets=[]
	current_movie= Movie(OMDB_data(each))
	for tweet in twitter_data(current_movie.director)['statuses']:
		current_tweet= Tweet(tweet)
		current_tweet.get_user_data()
		movie_tweets.append(current_tweet)
	current_movie.tweet_list = movie_tweets
	movies.append(current_movie)





#this is my squilite section creating a database.

conn = sqlite3.connect('tweets.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Tweets')
#this creates table structure 
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Tweets (tweet_id TEXT PRIMARY KEY, '
table_spec += 'user TEXT, movie_id TEXT, tweet_text TEXT, favorites INTEGER, retweets INTEGER)'
cur.execute(table_spec)


cur.execute('DROP TABLE IF EXISTS Users')
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Users (user_id TEXT PRIMARY KEY, '
table_spec += 'screen_name TEXT, favorites INTEGER)'
cur.execute(table_spec)


cur.execute('DROP TABLE IF EXISTS Movies')
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Movies (movie_id TEXT PRIMARY KEY, '
table_spec += 'title TEXT, director TEXT, languages INTEGER, rating REAL, top_paid_actor TEXT)'
cur.execute(table_spec)


for each in movies:
	statement = 'INSERT INTO Movies VALUES (?, ?, ?, ?, ?, ?)'
	cur.execute(statement, (each.movie_id, each.title, each.director, each.languages, each.rating, each.actors[0]))

	for each_tweet in each.tweet_list:
		statement = 'INSERT INTO Tweets VALUES (?, ?, ?, ?, ?, ?)'
		cur.execute(statement, (each_tweet.tweet_id, each_tweet.user, each.movie_id, each_tweet.tweet_text, each_tweet.favorites, each_tweet.retweets))
		statement= 'INSERT OR IGNORE INTO Users Values (?,?,?)'
		cur.execute(statement, (each_tweet.user, each_tweet.screen_name, each_tweet.user_favorites))



conn.commit()




with open("final_output.txt", "w") as outputFile:
	output = ""
	output += "---My Final Project---\n"

	#finding number of unique words for each movie
	for each in movies:
		unique_words=set()

		query= "SELECT tweet_text from Tweets where movie_id = ? "
		tweet_texts= cur.execute(query, (each.movie_id,)).fetchall()
		for each_tweet in tweet_texts:
			match= re.findall(r'(\S+)', each_tweet[0])
			if match:
				for each_word in match:
					unique_words.add(each_word)
		output += ("Number of unique words in tweets for {} is {}\n".format(each.title, len(unique_words)))
		

	# finding specific unique words in each movie
	for each in movies:
		unique_words=set()

		query= "SELECT tweet_text from Tweets where movie_id = ? "
		tweet_texts= cur.execute(query, (each.movie_id,)).fetchall()
		for each_tweet in tweet_texts:
			match= re.findall(r'(\S+)', each_tweet[0])
			if match:
				for each_word in match:
					unique_words.add(each_word)
		output += ("The unique words in tweets for {} is {}\n".format(each.title, unique_words))


	
#	finds screennames of users that have posted tweets with over 5 favorites.

	query= "SELECT screen_name from Users WHERE favorites > 5"
	more_than_5_favorites= cur.execute(query).fetchall()
	output += ("Screen name of tweets that have over 10 favorites {}\n". format(more_than_5_favorites))

	query = "SELECT title from Movies WHERE rating> 5 "
	ratings_= cur.execute(query).fetchall()
	output += ("Movies where rating is above 5.0 {}\n".format(ratings_))

	




	outputFile.write(output)
	outputFile.close()




# Put your tests here, with any edits you now need from when you turned them in with your project plan.
class Twitter(unittest.TestCase):
	def test1(self):
		self.assertEqual(type(twitter_data("Air Bud")), type({}))
	def test2(self):
		self.assertEqual(type(twitter_data("Air Bud")['statuses']), type ([]))
	def test3(self):
		self.assertTrue(len(twitter_data("Air Bud")['statuses']) >0)
	def test4(self):
		self.assertEqual(type(twitter_data("Air Bud")['statuses'][0]), type({}))
	def test5(self):
		twitter_data("Air Bud")
		path= os.path.exists("Air Bud.json")
		self.assertTrue(path)
	def test6(self):
		self.assertTrue(twitter_data("Air Bud")['statuses'][0].get("created_at", None))
	def test7(self):
		self.assertEqual(type(twitter_data("Air Bud")['statuses'][0].get("created_at", None)), type(""))
	def test8(self):
		self.assertTrue(twitter_data("Air Bud")['statuses'][0].get("text", None))
	def test9(self):
		twitter_user("18723984")
		path= os.path.exists("user_18723984.json")
		self.assertTrue(path)
class OMDB(unittest.TestCase):
	def test1(self):
		OMDB_data("Shrek")
		path= os.path.exists("movie_Shrek.json")
		self.assertTrue(path)
class Movies (unittest.TestCase):
	def test1(self):
		
		self.assertTrue(__str__("Shrek"), "My favorite movie is Shrek.")





# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)

#if __name__ == "__main__":
#	unittest.main(verbosity=2)



