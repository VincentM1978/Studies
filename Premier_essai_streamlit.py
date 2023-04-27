import streamlit as st


st.title('Outil de recommandation de films')

  
  

# multi select box
 
# first argument takes the box title
# second argument takes the options to show
genres = st.multiselect("Genres: ",
                         ['Drama', 'Action', 'Fantasy'])
 
# write the selected options
st.write("You selected", len(genres), 'genres')
