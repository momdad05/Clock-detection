# streamlit_app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Invisibility Cloak", layout="centered")
st.title("🧙 Invisibility Cloak (Streamlit demo)")

st.markdown("""
**How to use**

1. Stand *out of the camera frame* and press **Capture background**.  
2. Then step into frame holding a **white cloth/paper** and press **Capture cloak photo**.  
3. The app will replace the white area with the captured background.
""")

# initialize session state
if "background" not in st.session_state:
    st.session_state.background = None

col1, col2 = st.columns(2)

with col1:
    st.header("1) Capture background (empty)")
    bg_file = st.camera_input("Stand out of frame, then click to take background photo")
    if st.button("Capture background"):
        if bg_file is None:
            st.error("No photo taken. Use the camera input above to take the background photo.")
        else:
            bg_img = Image.open(bg_file).convert("RGB")
            bg = cv2.cvtColor(np.array(bg_img), cv2.COLOR_RGB2BGR)
            st.session_state.background = bg
            st.success("Background captured ✅")

with col2:
    st.header("2) Capture cloak photo")
    cloak_file = st.camera_input("Step into frame holding the cloak and take a photo")
    if cloak_file is not None and st.session_state.background is None:
        st.info("You captured a cloak photo but haven't captured the background yet. Capture background first.")

# Processing and result
if cloak_file is not None and st.session_state.background is not None:
    # Read images
    cloak_img = Image.open(cloak_file).convert("RGB")
    frame = cv2.cvtColor(np.array(cloak_img), cv2.COLOR_RGB2BGR)

    # Resize background to frame size (if needed)
    bg = st.session_state.background
    if (bg.shape[1], bg.shape[0]) != (frame.shape[1], frame.shape[0]):
        bg = cv2.resize(bg, (frame.shape[1], frame.shape[0]))

    # Convert to HSV and detect white (low S, high V)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Clean mask
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

    # Compose final image
    mask_inv = cv2.bitwise_not(mask)
    cloak_area = cv2.bitwise_and(bg, bg, mask=mask)
    rest = cv2.bitwise_and(frame, frame, mask=mask_inv)
    final = cv2.add(cloak_area, rest)

    # Show images side-by-side
    st.subheader("Result")
    st.image(cv2.cvtColor(final, cv2.COLOR_BGR2RGB), use_column_width=True)

# Controls
st.write("---")
if st.button("Clear background"):
    st.session_state.background = None
    st.experimental_rerun()