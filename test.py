import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2

class SimpleVideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        return img

webrtc_streamer(key="example", video_processor_factory=SimpleVideoTransformer)
