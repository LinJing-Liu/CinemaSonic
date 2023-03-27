import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler

from cosine_sim import *
import csv
import pandas as pd
from nltk.tokenize import TreebankWordTokenizer
import math

# precompute inverted index and idf
pd.set_option('max_colwidth', 600)
songs_df = pd.read_csv("../clean_song_dataset.csv")
movies_df = pd.read_csv("../clean_movie_dataset.csv")

# extract lyrics and movie tokens as list of strings
songs_df['tokens'] = songs_df["clean lyrics"].apply(eval)
movies_df['tokens'] = movies_df["clean about"].apply(eval)

# build inverted index of song lyrics
inverted_lyric_index = build_inverted_index(songs_df['tokens'])

# build idf
n_docs = songs_df.shape[0]
lyric_idf = compute_idf(inverted_lyric_index, n_docs)

# build norms
doc_norms = compute_doc_norms(inverted_lyric_index, lyric_idf, n_docs)


# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "060820Mollie!"
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this
def sql_search(movie):
    movie_lower = movie.lower()

    # 1. find matching movies in the database
    matching_movies = movies_df[movies_df['title'].str.lower() == movie_lower]

    # 2. If the movie has no matches:
    if matching_movies.shape[0] == 0:
        return json.dumps([])
    else:
        # 3. If the movie has matches:
        target_movie = matching_movies.iloc[0]
        movie_tokens = target_movie['tokens']
        movie_about = target_movie['about']
        
        ranked_cosine_score = index_search(
            movie_about.lower(),
            inverted_lyric_index,
            lyric_idf,
            doc_norms
            )
        
        first_25 = ranked_cosine_score[:25]
        first_25_index = [ind for _, ind in first_25]
        first_25_songs = songs_df.iloc[first_25_index].to_dict('index')
        song_list = result_to_json(first_25_songs)
        return json.dumps(song_list)


@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return sql_search(text)

app.run(debug=True)