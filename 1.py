import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
from collections import deque

# Initialize MediaPipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.65)
mpDraw = mp.solutions.drawing_utils

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

# Initialize webcam capture using Streamlit's in-built method
run = st.checkbox('Start Webcam')

if run:
    # Capture webcam input using OpenCV
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            st.write("Error: Unable to access the camera")
            break

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

            # Gesture to switch between colors
            if (thumb[1] - fore_finger[1] < 30):
                bpoints.append(deque(maxlen=512))
                blue_index += 1
                gpoints.append(deque(maxlen=512))
                green_index += 1
                rpoints.append(deque(maxlen=512))
                red_index += 1
                ypoints.append(deque(maxlen=512))
                yellow_index += 1

            # Clear the canvas when the button is pressed
            elif fore_finger[1] <= 65:
                if clear_button:  # Clear Button functionality
                    bpoints.clear()
                    gpoints.clear()
                    rpoints.clear()
                    ypoints.clear()
                    paintWindow[:] = 255

            # Append points to draw on the canvas
            else:
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(fore_finger)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(fore_finger)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(fore_finger)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(fore_finger)

        # Draw the points on the frame and the canvas
        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        # Display the frame and canvas using Streamlit's image function
        st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
        st.image(paintWindow[:, :, ::-1])  # Convert BGR to RGB for display

        # Stop the loop with a Streamlit button
        if st.button('Stop'):
            break

    cap.release()
    cv2.destroyAllWindows()
