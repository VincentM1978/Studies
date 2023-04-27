import streamlit as st
import pandas as pd

# load the movie dataset
df = pd.read_csv("movie_.csv")

st.title('Outil de recommandation de films')

# Text Input
name = st.text_input("Enter a name", "Type Here ...")

# Multi-select box
genres = st.multiselect("Genres: ", df['genres'].unique())

# Slider
level = st.slider("Sélectionnez une note minimale de film", 1, 10)

# Filter the dataset based on user input
filtered_df = df[(df['actors'].str.contains(name)) & 
                 (df['genres'].isin(genres)) &
                 (df['averageRating'] >= level)]

# Randomly select 3 movies from the filtered dataset
selected_movies = filtered_df.sample(3)

# Display the selected movies
st.write("Selected Movies:")
for index, row in selected_movies.iterrows():
    st.write(row['primaryTitle'], '(', row['startYear'], ')')
