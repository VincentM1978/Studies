import streamlit as st

st.title('RIMOUVEUR DE LA MORT')

image_upload = st.file_uploader("Choisissez une image", type = ['png', 'jpg', 'jpeg'])

if image_upload:
  st.download_button("Télécharger l'image", image_upload, "imagedl.jpg", mime="image")
