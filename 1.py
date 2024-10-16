import streamlit as st
from PIL import Image
import numpy as np

class Stegno:
    def encode(self, image, message):
        # Convert message to binary and add an end marker
        data = ''.join(format(ord(i), '08b') for i in message) + '1111111111111110'  # End marker
        img_data = np.array(image)

        # Check if the message can fit in the image
        if len(data) > img_data.size * 3:  # Each pixel has 3 channels (RGB)
            st.error("Message is too long to encode in this image.")
            return None

        data_index = 0
        for row in range(img_data.shape[0]):
            for col in range(img_data.shape[1]):
                pixel = list(img_data[row, col])
                for i in range(3):  # For RGB channels
                    if data_index < len(data):
                        # Modify LSB of the pixel safely
                        pixel[i] = (pixel[i] & ~1) | int(data[data_index])  # Set LSB
                        data_index += 1
                img_data[row, col] = tuple(pixel)
                if data_index >= len(data):  # Stop if all data is encoded
                    break

        return Image.fromarray(img_data)

    def decode(self, image):
        img_data = np.array(image)
        binary_data = ''

        for row in range(img_data.shape[0]):
            for col in range(img_data.shape[1]):
                pixel = img_data[row, col]
                binary_data += ''.join(str(pixel[i] & 1) for i in range(3))  # Get LSBs

        message = ''
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            if byte:
                message += chr(int(byte, 2))
            if message.endswith('\x00'):  # Stop at null character
                break

        return message.rstrip('\x00')

# Streamlit UI
st.title("Image Steganography")

option = st.selectbox("Choose an action:", ["Encode", "Decode"])

if option == "Encode":
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')  # Ensure the image is in RGB format
        st.image(image, caption='Uploaded Image', use_column_width=True)

        message = st.text_area("Enter the message to hide:")
        
        if st.button("Encode"):
            stego = Stegno()
            encoded_image = stego.encode(image, message)
            if encoded_image:
                st.image(encoded_image, caption='Encoded Image', use_column_width=True)
                encoded_image.save("encoded_image.png")
                st.success("Message encoded successfully!")

elif option == "Decode":
    uploaded_file = st.file_uploader("Upload an encoded image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')  # Ensure the image is in RGB format
        st.image(image, caption='Uploaded Encoded Image', use_column_width=True)

        if st.button("Decode"):
            stego = Stegno()
            hidden_message = stego.decode(image)
            st.text_area("Hidden Message:", hidden_message, height=200)
