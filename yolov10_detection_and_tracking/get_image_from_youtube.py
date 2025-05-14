from get_stream import stream_init
import cv2
import numpy as np

STREAM_URL = "https://www.youtube.com/watch?v=up3rJmxI1Fo"

def get_image_youtube():
    process, width, height = stream_init(STREAM_URL)
    if not process:
        print("Error: Unable to open stream.")
        return
    try:
        in_bytes = process.stdout.read(width * height * 3)
            
            # Erstelle ein beschreibbares Frame
        frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3]).copy()
        return frame
    
    finally:
        process.stdout.close()
        process.wait()
        cv2.destroyAllWindows()