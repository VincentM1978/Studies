import streamlit as st
from PIL import Image

from io import BytesIO

st.title("Détourage d'image")

image_upload = st.file_uploader("Choisissez une image", type = ['png', 'jpg', 'jpeg'])

def convert_image(image):
  buf = BytesIO()
  image.save(buf, format='PNG')
  byte_im = buf.getvalue()
  return byte_im
