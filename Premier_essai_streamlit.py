st.title("Détourage d'image")

image_upload = st.file_uploader("Choisissez une image", type = ['png', 'jpg', 'jpeg'])

def convert_image(image):
  buf = BytesIO()
  image.save(buf, format='PNG')
  byte_im = buf.getvalue()
  return byte_im

if image_upload:
  image = Image.open(image_upload)
  fixed = remove(image)
  downloadable_image = convert_image(fixed)
