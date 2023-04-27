import streamlit as st

st.title('Outil de recommandation de films')

  
 # Text Input
 
# save the input text in the variable 'name'
# first argument shows the title of the text input box
# second argument displays a default text inside the text input area
name = st.text_input("Enter a name", "Type Here ...")
 
# display the name when the submit button is clicked
# .title() is used to get the input text string
if(st.button('Submit')):
    result = name.title()
    st.success(result) 

# multi select box
 
# first argument takes the box title
# second argument takes the options to show
genres = st.multiselect("Genres: ",
                         ['Drama',
                          'Action', 
                          'Fantasy',
                          'Comedy',
                          'Romance',
                          'Thriller',
                          'Crime',
                          'Adventure',
                          'Horror',
                          'Mystery',
                          'Biography',
                          'Family',
                          'History',
                          'Animation',
                          'Sci-Fi',
                          'Documentary'])



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
