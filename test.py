import cv2
import streamlit as st

# Initialize webcam capture
cap = cv2.VideoCapture(0)

st.title("Webcam Test")

# Capture frame and display in Streamlit
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)

        # Show the frame in Streamlit
        st.image(frame, channels="BGR")
    else:
        st.write("Failed to capture image.")
else:
    st.write("Error: Unable to access webcam.")

# Release webcam
cap.release()
