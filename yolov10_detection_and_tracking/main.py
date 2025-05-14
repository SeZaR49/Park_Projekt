import cv2
import time
import numpy as np
from yolo_detector import YoloDetector
from tracker import Tracker
from get_stream import stream_init
from parking_manager import ParkingManager  # Import der erweiterten Klasse

MODEL_PATH = r"/home/park/ParkCode/Code/computer_vision/yolov10_detection_and_tracking/models/yolo11n.pt"

MAX_RETRIES = 5  # Maximale Anzahl an Wiederverbindungsversuchen
RETRY_DELAY = 3  # Wartezeit (Sekunden) vor erneutem Verbindungsversuch

def main():
    detector = YoloDetector(model_path=MODEL_PATH, confidence=0.2)
    tracker = Tracker()
    parking_manager = ParkingManager(position_tolerance=5, countdown_duration=30)

    retry_count = 0  # Zählt die Verbindungsabbrüche

    while retry_count < MAX_RETRIES:
        print(f"🔄 Starte Kamera-Stream... (Versuch {retry_count + 1}/{MAX_RETRIES})")
        process, width, height = stream_init()
        
        if not process:
            print("❌ Fehler: Konnte den Stream nicht öffnen.")
            return
        
        try:
            while True:
                # 🔥 Versuche, alte Frames zu verwerfen, aber stoppe nicht den Stream!
                for _ in range(5):  # Maximal 5 alte Frames verwerfen
                    temp_bytes = process.stdout.read(width * height * 3)
                    if not temp_bytes:
                        break  # Falls kein neues Bild kommt, nicht weiter warten

                # Jetzt holen wir das aktuellste Frame:
                in_bytes = process.stdout.read(width * height * 3)



                if not in_bytes:
                    print(f"⚠️ Stream-Verlust erkannt! Versuch {retry_count + 1}/{MAX_RETRIES}")
                    retry_count += 1
                    process.stdout.close()
                    process.wait()
                    time.sleep(RETRY_DELAY)
                    break  # Verlasse die Schleife und starte `stream_init()` neu
                
                # Frame einlesen und RGB → BGR konvertieren für OpenCV
                frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # YOLO-Detektion
                start_time = time.perf_counter()
                detections = detector.detect(frame)

                if not detections:
                    print("⚠️ Warnung: YOLO erkennt keine Objekte!")

                tracking_ids, boxes = tracker.track(detections, frame)

                for tracking_id, bounding_box in zip(tracking_ids, boxes):
                    parking_manager.update_position(tracking_id, bounding_box)
                    parking_manager.reset_if_moved(tracking_id, bounding_box)

                    status = parking_manager.get_status(tracking_id)

                    if tracking_id not in parking_manager.parked_ids:
                        cv2.putText(frame, f"ID {tracking_id}: {status}", 
                                    (int(bounding_box[0]), int(bounding_box[1] - 5)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)

                    color = (0, 255, 0) if tracking_id in parking_manager.parked_ids else (0, 0, 255)
                    cv2.rectangle(frame, (int(bounding_box[0]), int(bounding_box[1])),
                                  (int(bounding_box[2]), int(bounding_box[3])),
                                  color, 2)

                end_time = time.perf_counter()
                fps = 1 / (end_time - start_time)
                print(f"⚡ Current FPS: {fps:.2f}")

                # Zeige das Bild an
                cv2.imshow("Frame", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    print("👋 Beende Programm...")
                    return
        except Exception as e:
            print(f"❌ Fehler: {e}")

        # Warte bevor ein neuer Versuch gestartet wird
        time.sleep(RETRY_DELAY)

    print("🚨 Maximale Anzahl an Wiederverbindungsversuchen erreicht. Beende Programm.")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
