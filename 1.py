import streamlit as st
from PIL import Image
from io import BytesIO
import os

class StegnoStreamlit:

    def main(self):
        st.title("Image Steganography")

        # Main page with Encode/Decode buttons
        option = st.selectbox("Choose an action", ["Encode", "Decode"])

        if option == "Encode":
            self.frame1_encode()
        elif option == "Decode":
            self.frame1_decode()

    def frame1_decode(self):
        st.subheader("Decode hidden text from an image")
        uploaded_file = st.file_uploader("Select an image to decode", type=["png", "jpeg", "jpg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Selected Image", use_column_width=True)

            hidden_data = self.decode(image)
            st.write("Hidden data is:")
            st.text_area("Decoded Text", hidden_data)

    def frame1_encode(self):
        st.subheader("Encode text into an image")
        uploaded_file = st.file_uploader("Select an image to encode", type=["png", "jpeg", "jpg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Selected Image", use_column_width=True)

            text_data = st.text_area("Enter the message to hide")
            if st.button("Encode"):
                if text_data:
                    new_img = self.encode_enc(image, text_data)
                    if new_img:
                        buf = BytesIO()
                        new_img.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        st.download_button(
                            label="Download Encoded Image",
                            data=byte_im,
                            file_name="image_with_hidden_text.png",
                            mime="image/png"
                        )
                        st.success("Encoding Successful!")
                else:
                    st.error("Please enter some text to encode.")

    def decode(self, image):
        data = ''
        imgdata = iter(image.getdata())

        while True:
            pixels = [value for value in imgdata.__next__()[:3] +
                      imgdata.__next__()[:3] +
                      imgdata.__next__()[:3]]
            binstr = ''
            for i in pixels[:8]:
                if i % 2 == 0:
                    binstr += '0'
                else:
                    binstr += '1'

            data += chr(int(binstr, 2))
            if pixels[-1] % 2 != 0:
                return data

    def genData(self, data):
        newd = []
        for i in data:
            newd.append(format(ord(i), '08b'))
        return newd

    def modPix(self, pix, data):
        datalist = self.genData(data)
        lendata = len(datalist)
        imdata = iter(pix)

        for i in range(lendata):
            pixels = [value for value in imdata.__next__()[:3] +
                      imdata.__next__()[:3] +
                      imdata.__next__()[:3]]

            for j in range(8):
                if datalist[i][j] == '0' and pixels[j] % 2 != 0:
                    pixels[j] -= 1
                elif datalist[i][j] == '1' and pixels[j] % 2 == 0:
                    pixels[j] -= 1

            if i == lendata - 1:
                if pixels[-1] % 2 == 0:
                    pixels[-1] -= 1
            else:
                if pixels[-1] % 2 != 0:
                    pixels[-1] -= 1

            pixels = tuple(pixels)
            yield pixels[:3]
            yield pixels[3:6]
            yield pixels[6:9]

    def encode_enc(self, image, data):
        new_image = image.copy()
        w = new_image.size[0]
        (x, y) = (0, 0)

        for pixel in self.modPix(new_image.getdata(), data):
            new_image.putpixel((x, y), pixel)
            if x == w - 1:
                x = 0
                y += 1
            else:
                x += 1

        return new_image

# Run the app
stegno_app = StegnoStreamlit()
stegno_app.main()
