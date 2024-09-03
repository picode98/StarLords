# This is BigPixel MVP Pi code to add some interactivity (as a placeholder for 
# the development of StarLords game code) by presenting webcam frames 
# to the BigPixel display using E1.31 over an Ethernet connection between 
# the Pi brain and an ethernet equipped Dig-Quad ESP-32 WLED receiver node

import cv2           # python3-openCV computer vision for Webcam
import sacn          # Art-Net and E1.31 ethernet LED frame transmission
import numpy as np   # math

# Constants for matrix configuration
ARRAY_WIDTH = 16  # Width of the matrix
ARRAY_HEIGHT = 16  # Height of the matrix
COLOR_DEPTH = 'RGB'  # Choose either 'RGB' or 'RGBW'

# Calculate channels per pixel
if COLOR_DEPTH == 'RGB':
    CHANNELS_PER_PIXEL = 3
elif COLOR_DEPTH == 'RGBW':
    CHANNELS_PER_PIXEL = 4
else:
    raise ValueError("COLOR_DEPTH must be 'RGB' or 'RGBW'.")

# Total number of pixels
TOTAL_PIXELS = ARRAY_WIDTH * ARRAY_HEIGHT

# Total number of DMX channels needed
TOTAL_CHANNELS = TOTAL_PIXELS * CHANNELS_PER_PIXEL

# Each E1.31 universe can hold 512 DMX channels
CHANNELS_PER_UNIVERSE = 512

# Calculate the number of universes needed
TOTAL_UNIVERSES = (TOTAL_CHANNELS + CHANNELS_PER_UNIVERSE - 1) // CHANNELS_PER_UNIVERSE

# Initialize the sACN E1.31 sender
sender = sacn.sACNsender()
sender.start()

# Activate universes dynamically based on total universes needed
for universe_id in range(1, TOTAL_UNIVERSES + 1):
    sender.activate_output(universe_id)
    sender[universe_id].unicast = True  # Set to multicast or unicast based on your setup

# Function to convert RGB to RGBW if necessary
def rgb_to_rgbw(image):
    # Split the image into its R, G, B channels
    R, G, B = cv2.split(image)

    # Calculate the white component as the minimum of R, G, B
    W = np.minimum(np.minimum(R, G), B)

    # Subtract W from R, G, B to get the remaining RGB components
    R = R - W
    G = G - W
    B = B - W

    # Merge the adjusted R, G, B channels back together with the W channel
    rgbw_image = cv2.merge([R, G, B, W])

    return rgbw_image

# Initialize the webcam
webcam = cv2.VideoCapture(0)

try:
    while True:
        # Capture a frame from the webcam
        ret, frame = webcam.read()

        if not ret:
            break

        # Resize the frame to match the matrix size
        frame_resized = cv2.resize(frame, (ARRAY_WIDTH, ARRAY_HEIGHT))

        # Convert to RGB if OpenCV provides the image in BGR
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        # If the color depth is RGBW, convert the frame
        if COLOR_DEPTH == 'RGBW':
            frame_rgbw = rgb_to_rgbw(frame_rgb)
        else:
            frame_rgbw = frame_rgb

        # Flatten the image into a list of pixel values
        pixel_data = frame_rgbw.flatten().tolist()

        # Send pixel data across universes
        for universe_id in range(1, TOTAL_UNIVERSES + 1):
            start_channel = (universe_id - 1) * CHANNELS_PER_UNIVERSE
            end_channel = min(universe_id * CHANNELS_PER_UNIVERSE, TOTAL_CHANNELS)

            # Assign DMX data to the current universe
            sender[universe_id].dmx_data = pixel_data[start_channel:end_channel]

        # Wait to maintain frame rate, adjust as needed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

finally:
    # Cleanup resources
    webcam.release()
    cv2.destroyAllWindows()
    sender.stop()
