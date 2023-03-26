import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler

from cosine_sim import build_inverted_index, compute_idf, compute_doc_norms, accumulate_dot_scores, text_to_term_dict, index_search
import csv
import pandas as pd
from nltk.tokenize import TreebankWordTokenizer
import math

# precompute inverted index and idf
pd.set_option('max_colwidth', 600)
songs_df = pd.read_csv("../spotify_millsongdata.csv")

song_names = list(songs_df["song"])
data = list(songs_df["text"])
clean_data = [i.replace('\n','').replace('\r','') for i in data]

tokenized_data = [lyrics.lower().split() for lyrics in clean_data]

# build inverted index of song lyrics
inverted_lyric_index = build_inverted_index(tokenized_data)

# build idf
n_docs = len(clean_data)
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
def sql_search(episode):
    episode_lower = episode.lower()
    ranked_cosine_score = index_search(
        episode_lower,
        inverted_lyric_index,
        lyric_idf,
        doc_norms
        )
    
    first_five_scores = ranked_cosine_score[:5]
    #first_five_data = [[song_names[i], clean_data[i]] for score, i in ranked_cosine_score]

    # query_sql = f"""SELECT * FROM episodes WHERE LOWER( title ) LIKE '%%{episode.lower()}%%' limit 10"""
    keys = ["name","lyrics"]
    good_songs = [[song_names[i], clean_data[i]] for score, i in ranked_cosine_score]
    print(good_songs)
    
    return json.dumps([dict(zip(keys,i)) for i in good_songs])

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return sql_search(text)

app.run(debug=True)