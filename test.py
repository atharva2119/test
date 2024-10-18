import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
from collections import deque
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

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


# Video Processor Class to handle frame-by-frame processing
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        # Instance variables for tracking drawn points
        self.bpoints = [deque(maxlen=1024)]
        self.gpoints = [deque(maxlen=1024)]
        self.rpoints = [deque(maxlen=1024)]
        self.ypoints = [deque(maxlen=1024)]
        self.blue_index = self.green_index = self.red_index = self.yellow_index = 0
        self.paintWindow = np.zeros((471, 636, 3)) + 255

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")

        # Flip and convert image for hand detection
        frame_rgb = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    lmx = int(lm.x * image.shape[1])
                    lmy = int(lm.y * image.shape[0])
                    landmarks.append([lmx, lmy])
                mpDraw.draw_landmarks(image, handslms, mpHands.HAND_CONNECTIONS)

            fore_finger = (landmarks[8][0], landmarks[8][1])
            thumb = (landmarks[4][0], landmarks[4][1])

            if (thumb[1] - fore_finger[1] < 30):  # Condition to start a new line
                self.bpoints.append(deque(maxlen=512))
                self.blue_index += 1
                self.gpoints.append(deque(maxlen=512))
                self.green_index += 1
                self.rpoints.append(deque(maxlen=512))
                self.red_index += 1
                self.ypoints.append(deque(maxlen=512))
                self.yellow_index += 1

            elif fore_finger[1] <= 65 and clear_button:  # Clear functionality
                self.bpoints.clear()
                self.gpoints.clear()
                self.rpoints.clear()
                self.ypoints.clear()
                self.paintWindow[:] = 255

            else:
                if colorIndex == 0:
                    self.bpoints[self.blue_index].appendleft(fore_finger)
                elif colorIndex == 1:
                    self.gpoints[self.green_index].appendleft(fore_finger)
                elif colorIndex == 2:
                    self.rpoints[self.red_index].appendleft(fore_finger)
                elif colorIndex == 3:
                    self.ypoints[self.yellow_index].appendleft(fore_finger)

        # Draw points on frame
        points = [self.bpoints, self.gpoints, self.rpoints, self.ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(image, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv2.line(self.paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        return image


# Initialize the WebRTC streamer
webrtc_streamer(key="example", video_processor_factory=VideoProcessor)
