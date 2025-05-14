import cv2
import time
import numpy as np
from yolo_detector import YoloDetector
from tracker import Tracker
#from get_stream import stream_init
from parking_manager import ParkingManager  # Import der erweiterten Klasse
from get_camera import capture_image
#from get_image_from_youtube import get_image_youtube

MODEL_PATH = r"/home/park/ParkCode/Code/computer_vision/yolov10_detection_and_tracking/models/yolo11n.pt"


def main():
    detector = YoloDetector(model_path=MODEL_PATH, confidence=0.2)
    tracker = Tracker()
    parking_manager = ParkingManager(position_tolerance=5, countdown_duration=30)

    """
    process, width, height = capture_image()
    if not process:
        print("Error: Unable to open stream.")
        return 
    """

    while True:
        frame, width, height  = capture_image()
        print( "frame type1:")
        print(type(frame))

        #start_time = time.perf_counter()
        detections = detector.detect(frame)
        tracking_ids, boxes = tracker.track(detections, frame)

        for tracking_id, bounding_box in zip(tracking_ids, boxes):
            # Aktualisiere die Position
            parking_manager.update_position(tracking_id, bounding_box)
            parking_manager.reset_if_moved(tracking_id, bounding_box)

            # Status abrufen
            status = parking_manager.get_status(tracking_id)

            # Blaue Schrift nur anzeigen, wenn das Fahrzeug nicht geparkt ist
            if tracking_id not in parking_manager.parked_ids:
                cv2.putText(frame, f"ID {tracking_id}: {status}", 
                            (int(bounding_box[0]), int(bounding_box[1] - 5)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)

            # Zeichne die Bounding Box
            color = (0, 255, 0) if tracking_id in parking_manager.parked_ids else (0, 0, 255)
            cv2.rectangle(frame, (int(bounding_box[0]), int(bounding_box[1])),
                            (int(bounding_box[2]), int(bounding_box[3])),
                            color, 2)

        end_time = time.perf_counter()
        fps = 1 / (end_time - start_time)
        print(f"Current fps: {fps}")

        # Skalieren des Frames auf eine kleinere Größe
        smaller_frame = cv2.resize(frame, (1080, 620))  # Skaliere das Bild auf 920x1080

        # Zeige das verkleinerte Bild
        cv2.imshow("Frame", smaller_frame)  # Hier wird das kleinere Bild angezeigt

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break


if __name__ == "__main__":
    main()
