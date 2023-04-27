import streamlit as st


st.title('Outil de recommandation de films')

  
  

# multi select box
 
# first argument takes the box title
# second argument takes the options to show
genres = st.multiselect("Genres: ",
                         ['Drama', 'Action', 'Fantasy', 'Comedy', 'Romance', 'Thriller', 'Crime', 'Adventure', 'Horror', 'Mystery', 'Biography', 'Family', 'History', 'Animation'])

Drama          8289
Comedy         3920
Action         2155
Romance        1962
Thriller       1836
Crime          1765
Adventure      1456
Horror          940
Mystery         863
Biography       693
Fantasy         659
Family          647
History         558
Animation       430
Sci-Fi          429
Documentary     333
Adult             1

# write the selected options
st.write("You selected", len(genres), 'genres')


# slider
 
# first argument takes the title of the slider
# second argument takes the starting of the slider
# last argument takes the end number
level = st.slider("Sélectionnez une note minimale de film", 1, 10)
 
# print the level
# format() is used to print value
# of a variable at a specific position
st.text('Selected: {}'.format(level))
