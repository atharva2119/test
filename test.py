import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
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

# Streamlit UI setup
st.title("Air Canvas - AR Whiteboard")
st.sidebar.title("Controls")
clear_button = st.sidebar.button("Clear Canvas")
color_choice = st.sidebar.selectbox("Choose Color", ["Blue", "Green", "Red", "Yellow"])

# Map color choice to index
color_map = {"Blue": 0, "Green": 1, "Red": 2, "Yellow": 3}
colorIndex = color_map.get(color_choice)

# Define video transformer for WebRTC streaming
class HandTrackerVideoTransformer(VideoTransformerBase):
    def __init__(self):
        super().__init__()

    def transform(self, frame):
        global blue_index, green_index, red_index, yellow_index, bpoints, gpoints, rpoints, ypoints

        # Convert frame to RGB
        frame_rgb = cv2.cvtColor(frame.to_ndarray(), cv2.COLOR_BGR2RGB)
        
        # Process the frame to detect hands
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    lmx = int(lm.x * frame_rgb.shape[1])
                    lmy = int(lm.y * frame_rgb.shape[0])
                    landmarks.append([lmx, lmy])
                mpDraw.draw_landmarks(frame_rgb, handslms, mpHands.HAND_CONNECTIONS)

            fore_finger = (landmarks[8][0], landmarks[8][1])
            thumb = (landmarks[4][0], landmarks[4][1])

            # Check if thumb and forefinger are close enough (drawing gesture)
            if (thumb[1] - fore_finger[1] < 30):
                bpoints.append(deque(maxlen=512))
                blue_index += 1
                gpoints.append(deque(maxlen=512))
                green_index += 1
                rpoints.append(deque(maxlen=512))
                red_index += 1
                ypoints.append(deque(maxlen=512))
                yellow_index += 1

            # Clear the canvas if the clear button is pressed
            elif clear_button:
                bpoints.clear()
                gpoints.clear()
                rpoints.clear()
                ypoints.clear()

            else:
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(fore_finger)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(fore_finger)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(fore_finger)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(fore_finger)

        # Draw points on the frame
        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame_rgb, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

# Start WebRTC streamer
webrtc_streamer(key="canvas", video_transformer_factory=HandTrackerVideoTransformer)
