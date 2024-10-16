import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
import time
from collections import deque

# Cache MediaPipe model loading to avoid reloading on each interaction
@st.experimental_singleton
def load_hand_model():
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.65)
    mpDraw = mp.solutions.drawing_utils
    return hands, mpDraw

hands, mpDraw = load_hand_model()

# Set up color points
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

# Color indices
blue_index = green_index = red_index = yellow_index = 0

# Colors for drawing
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

# Create a blank canvas
paintWindow = np.zeros((471, 636, 3)) + 255

# Streamlit UI setup
st.title("Air Canvas - AR Whiteboard")
st.sidebar.title("Controls")

clear_button = st.sidebar.button("Clear Canvas")
color_choice = st.sidebar.selectbox("Choose Color", ["Blue", "Green", "Red", "Yellow"])

# Map color choice to index
color_map = {"Blue": 0, "Green": 1, "Red": 2, "Yellow": 3}
colorIndex = color_map.get(color_choice)

# Initialize webcam capture
cap = cv2.VideoCapture(0)

# Set webcam resolution lower for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Main loop to process frames
while True:
    ret, frame = cap.read()
    if not ret:
        st.write("Error accessing webcam.")
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get hand landmark prediction
    result = hands.process(framergb)

    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                lmx = int(lm.x * frame.shape[1])
                lmy = int(lm.y * frame.shape[0])
                landmarks.append([lmx, lmy])
            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

        fore_finger = (landmarks[8][0], landmarks[8][1])
        thumb = (landmarks[4][0], landmarks[4][1])

        # If thumb is close to the index finger, consider it a gesture to change color
        if (thumb[1] - fore_finger[1] < 30):
            bpoints.append(deque(maxlen=512))
            blue_index += 1
            gpoints.append(deque(maxlen=512))
            green_index += 1
            rpoints.append(deque(maxlen=512))
            red_index += 1
            ypoints.append(deque(maxlen=512))
            yellow_index += 1

        # Check for Clear Canvas button press
        elif fore_finger[1] <= 65:
            if clear_button:
                bpoints.clear()
                gpoints.clear()
                rpoints.clear()
                ypoints.clear()
                paintWindow[:] = 255

        # Add points to the corresponding deque based on selected color
        else:
            if colorIndex == 0:
                bpoints[blue_index].appendleft(fore_finger)
            elif colorIndex == 1:
                gpoints[green_index].appendleft(fore_finger)
            elif colorIndex == 2:
                rpoints[red_index].appendleft(fore_finger)
            elif colorIndex == 3:
                ypoints[yellow_index].appendleft(fore_finger)

    # Draw on canvas and display in Streamlit
    points = [bpoints, gpoints, rpoints, ypoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

    # Show the webcam frame and canvas using Streamlit's image function
    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
    st.image(paintWindow[:, :, ::-1])  # Convert BGR to RGB for display

    # Add a Stop button to exit the loop
    if st.button('Stop'):
        break

    # Add a small delay to reduce CPU/GPU usage
    time.sleep(0.1)

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
