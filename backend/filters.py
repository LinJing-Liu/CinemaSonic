import pandas as pd
from enum import Enum
"""
Filtering Functions

This file contains functions that filter song results based on 
user's input. 

Functions take in a pandas data frame, and returns a filtered data
frame.
"""

def filter_by_popularity(df, option, threshold=50):
	if option == 1: # select niche
		return df[df.track_popularity < threshold]
	elif option == 2: # anything
		return df
	elif option == 3: # select popular
		return df[df.track_popularity >= threshold]
	else:
		raise ValueError("The popularity filter selection is invalid")

def filter_by_song_length(df, option, threshold=180000):
	if option == 1: # select short
		return df[df.duration_ms < threshold]
	elif option == 2: # anything
		return df
	elif option == 3: # long
		return df[df.duration_ms >= threshold]
	else:
		raise ValueError("The song length filter selection is invalid")


def filter_by_genre(df, cosine_scores, genres=[]):
    genres = genres.lower().split(',')
    if "rnb" in genres:
        genres.append('r&b')

    total_songs = 0
    ind = 0
    shape = df.shape[0]

    first_25_index = []
    while total_songs < 25 and ind < shape:
        _, song_index = cosine_scores[ind]
        song_info = df.iloc[song_index]

        if song_info.playlist_genre.lower() in genres:
            first_25_index.append(song_index)
            total_songs += 1
        ind += 1
    
    first_25_songs = df.iloc[first_25_index].to_dict('index')
    print(first_25_index)

    return (first_25_index, first_25_songs)

def filter_df(df, filter_func, param, threshold=None):
	if threshold == None:
		return filter_func(df, param)
	else:
		return filter_func(df, param, threshold=threshold)

# # precompute inverted index and idf
# pd.set_option('max_colwidth', 600)
# songs_df = pd.read_csv("clean_spotify.csv")
# movies_df = pd.read_csv("clean_movie_dataset.csv")

# # extract lyrics and movie tokens as list of strings
# songs_df['tokens'] = songs_df["clean lyrics"].apply(eval)
# movies_df['tokens'] = movies_df["clean about"].apply(eval)

# filtered_songs = filter_by_popularity(songs_df, 1)
# print(filtered_songs['playlist_genre'])
