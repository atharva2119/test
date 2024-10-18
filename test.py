import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
from collections import deque
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Initialize Mediapipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.65)
mpDraw = mp.solutions.drawing_utils

# Colors for drawing
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]

# Define Air Canvas video processor class
class AirCanvasProcessor(VideoTransformerBase):
    def __init__(self):
        self.bpoints = [deque(maxlen=1024)]
        self.gpoints = [deque(maxlen=1024)]
        self.rpoints = [deque(maxlen=1024)]
        self.ypoints = [deque(maxlen=1024)]

        # Color indices
        self.blue_index = self.green_index = self.red_index = self.yellow_index = 0

        # Create a blank canvas
        self.paintWindow = np.zeros((471, 636, 3)) + 255
        self.colorIndex = 0

    def process(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        framergb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Get hand landmark prediction
        result = hands.process(framergb)
        
        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    lmx = int(lm.x * img.shape[1])
                    lmy = int(lm.y * img.shape[0])
                    landmarks.append([lmx, lmy])
                mpDraw.draw_landmarks(img, handslms, mpHands.HAND_CONNECTIONS)

            # Use index finger and thumb for drawing
            fore_finger = (landmarks[8][0], landmarks[8][1])
            thumb = (landmarks[4][0], landmarks[4][1])

            if (thumb[1] - fore_finger[1] < 30):
                # New point: reset deque for a new stroke
                self.bpoints.append(deque(maxlen=512))
                self.blue_index += 1
                self.gpoints.append(deque(maxlen=512))
                self.green_index += 1
                self.rpoints.append(deque(maxlen=512))
                self.red_index += 1
                self.ypoints.append(deque(maxlen=512))
                self.yellow_index += 1

            else:
                # Draw based on current color index
                if self.colorIndex == 0:
                    self.bpoints[self.blue_index].appendleft(fore_finger)
                elif self.colorIndex == 1:
                    self.gpoints[self.green_index].appendleft(fore_finger)
                elif self.colorIndex == 2:
                    self.rpoints[self.red_index].appendleft(fore_finger)
                elif self.colorIndex == 3:
                    self.ypoints[self.yellow_index].appendleft(fore_finger)

        # Draw the strokes on the canvas
        points = [self.bpoints, self.gpoints, self.rpoints, self.ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(img, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv2.line(self.paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        return img

# Streamlit app interface
st.title("Air Canvas - AR Whiteboard")

# Sidebar for control options
st.sidebar.title("Controls")
clear_button = st.sidebar.button("Clear Canvas")
color_choice = st.sidebar.selectbox("Choose Color", ["Blue", "Green", "Red", "Yellow"])

# Map color choice to index
color_map = {"Blue": 0, "Green": 1, "Red": 2, "Yellow": 3}
processor = AirCanvasProcessor()
processor.colorIndex = color_map.get(color_choice)

if clear_button:
    processor.bpoints = [deque(maxlen=1024)]
    processor.gpoints = [deque(maxlen=1024)]
    processor.rpoints = [deque(maxlen=1024)]
    processor.ypoints = [deque(maxlen=1024)]
    processor.paintWindow[:] = 255

# Use webrtc_streamer to capture video
webrtc_streamer(key="canvas", video_processor_factory=lambda: processor)
