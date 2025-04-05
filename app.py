import streamlit as st
import pickle
import pandas as pd
import requests
import time
from requests.exceptions import RequestException

def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=7a8fcb7c2e6543561e594c575c62f0a6&language=en-US'
    retries = 3
    wait_time = 1

    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for bad status codes
            data = response.json()
            if 'poster_path' in data and data['poster_path']:
                return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
            else:
                print(f"No poster path found for movie ID: {movie_id}")
                return "https://via.placeholder.com/150" # Placeholder image
        except RequestException as e:
            print(f"Request failed: {e} for movie ID: {movie_id}")
            if attempt < retries - 1:
                time.sleep(wait_time)
                wait_time *= 2
            else:
                print("Max retries reached. Giving up.")
                return None  # Or a placeholder

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:  # Handle the case where the movie is not found
        st.error(f"Movie '{movie}' not found in the dataset.")
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters


# Load data (make sure paths are correct)
try:
    movies_list = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_list)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Movie data files (pickle files) not found. Make sure they are in the correct directory.")
    st.stop()  # Stop execution if data files are missing

selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    if names and posters: #Check if names and posters are not empty
        num_cols = min(len(names), 5)  # Limit to 5 columns
        cols = st.columns(num_cols)

        for i in range(num_cols):
            with cols[i]:
                st.text(names[i])
                if posters[i]: # Check if poster is available before displaying
                    st.image(posters[i])
                else:
                    st.write("Poster not available") # Display message if poster is unavailable