import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler

from cosine_sim import *
import pandas as pd
import nltk
from nltk.tokenize import TreebankWordTokenizer



# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))
print(os.environ['ROOT_PATH'])

# precompute inverted index and idf
pd.set_option('max_colwidth', 600)
songs_df = pd.read_csv("clean_song_dataset.csv")
movies_df = pd.read_csv("clean_movie_dataset.csv")

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


# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
# MYSQL_USER = "root"
# MYSQL_USER_PASSWORD = "MayankRao16Cornell.edu"
# MYSQL_PORT = 3306
# MYSQL_DATABASE = "kardashiandb"

# mysql_engine = MySQLDatabaseHandler(
#     MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)

# # Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
# mysql_engine.load_file_into_db()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded,
# but if you decide to use SQLAlchemy ORM framework,
# there's a much better and cleaner way to do this


@app.route('/get_output/<movie>/<director>/<actors>/<genre>')
def sql_search(movie,director,actors,genre):
    movie_lower = movie.lower()
    director = director.lower()
    actors = actors.lower()
    genre = genre.lower()
    
    # 1. find matching movies in the database
    dataset_titles = movies_df['title']
    matching_movies = movies_df[dataset_titles == movie_lower]

    # Return no result found if the movie title input is empty
    if (movie_lower == 'a'):
        return json.dumps([])
    
    # 2. If the movie has no matches:
    if matching_movies.shape[0] == 0:
        
        edit_dist = np.array([nltk.edit_distance(movie_lower,title) for title in dataset_titles])

        if np.min(edit_dist) <= 5:
            matched_title = dataset_titles[np.argmin(edit_dist)]
            return result_json(movies_df[dataset_titles == matched_title]) 
        
        else:
            if genre != "select a genre":
                dataset_genres = set([g for lst in movies_df['genre'] for g in lst])
                edit_dist_genres = np.array([nltk.edit_distance(genre,genres) for genres in dataset_genres])
                genre = dataset_genres[np.argmin(edit_dist_genres)]
                               
                if director == 'a':
                    genres_of_movies = movies_df['genre']
                    bool_lst = [genre in lst for lst in genres_of_movies]
                    
                    return result_json(movies_df[bool_lst])
                
                else:
                    dataset_directors = movies_df['director']
                    edit_dist_directors = np.array([nltk.edit_distance(director,directors) for directors in dataset_directors])
                    director = dataset_directors[np.argmin(edit_dist_directors)]
                    
                    matched_director = movies_df[dataset_directors == director]
                    
                    # if matched_director.empty:
                    #     genres_of_movies = movies_df['genre'].apply(lambda x: x.lower().split(',') if type(x)!= float else str(x))
                    #     bool_lst = [genre in lst for lst in genres_of_movies]
                        
                    #     return result_json(movies_df[bool_lst])
                    
                    genres_of_director_movies = matched_director['genre']
                    bool_lst = [genre in lst for lst in genres_of_director_movies]
                    
                    if sum(bool_lst) == 0:
                        return result_json(matched_director)
                     
                    return result_json(matched_director[bool_lst])

            
            else:
                if director == 'a':
                    matched_title = dataset_titles[np.argmin(edit_dist)]
                    return result_json(movies_df[dataset_titles == matched_title])

                else:
                    dataset_directors = movies_df['director']
                    edit_dist_directors = np.array([nltk.edit_distance(director,directors) for directors in dataset_directors])
                    director = dataset_directors[np.argmin(edit_dist_directors)]
                    return result_json(movies_df[dataset_directors == director])
                    
                
                
        return json.dumps([])
    else:
        
        return result_json(matching_movies)
        # # 3. If the movie has matches:
        # target_movie = matching_movies.iloc[0]
        # movie_tokens = target_movie['tokens']
        # movie_about = target_movie['about']

        # ranked_cosine_score = index_search(
        #     movie_about.lower(),
        #     inverted_lyric_index,
        #     lyric_idf,
        #     doc_norms
        # )

        # first_25 = ranked_cosine_score[:25]
        # first_25_index = [ind for _, ind in first_25]
        # first_25_songs = songs_df.iloc[first_25_index].to_dict('index')
        # song_list = result_to_json(first_25_songs)
        # return json.dumps(song_list)


def result_json(matching_movies):
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
    
    
MOVIEGENRELIST = ["Action", "Adventure", "Comedy", "Drama",
                  "Fantasy", "Horror", "Romance", "Sci-fi", "Thriller", "Other"]


@app.route("/")
def home():
    return render_template('base.html', movieGenres=MOVIEGENRELIST)


@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return sql_search(text)


app.run(debug=True)
