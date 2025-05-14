import time
import numpy as np

class ParkingManager:
    def __init__(self, position_tolerance=5, countdown_duration=30):
        self.last_position = {}
        self.last_time = {}
        self.countdown_started = {}
        self.parked_ids = set()  # IDs der Fahrzeuge, die als Parkplätze deklariert sind
        self.position_tolerance = position_tolerance
        self.countdown_duration = countdown_duration

    def update_position(self, tracking_id, position):
        if tracking_id in self.parked_ids:
            # Fahrzeug wurde bereits als Parkplatz deklariert -> Ignorieren
            return

        position = np.array(position)
        if tracking_id not in self.last_position:
            # Erstes Mal tracken
            self.last_position[tracking_id] = position
            self.last_time[tracking_id] = time.time()
            self.countdown_started[tracking_id] = False
        else:
            # Berechne Distanz zur letzten Position
            distance = np.linalg.norm(self.last_position[tracking_id] - position)

            if distance <= self.position_tolerance:
                # Fahrzeug steht still
                if not self.countdown_started[tracking_id]:
                    if time.time() - self.last_time[tracking_id] > 10:  # Stillstand > 10 Sek
                        self.countdown_started[tracking_id] = True
            else:
                # Fahrzeug bewegt sich -> Timer zurücksetzen
                self.last_position[tracking_id] = position
                self.last_time[tracking_id] = time.time()
                self.countdown_started[tracking_id] = False

            # Prüfe Countdown
            if self.countdown_started[tracking_id]:
                countdown = int(self.countdown_duration - (time.time() - self.last_time[tracking_id]))
                if countdown <= 0:
                    self.parked_ids.add(tracking_id)  # Fahrzeug als Parkplatz deklarieren
                    self.countdown_started[tracking_id] = False

    def get_status(self, tracking_id):
        """ Gibt den aktuellen Status eines Fahrzeugs zurück. """
        if tracking_id in self.parked_ids:
            return "Parkplatz gespeichert"
        if self.countdown_started.get(tracking_id, False):
            countdown = int(self.countdown_duration - (time.time() - self.last_time[tracking_id]))
            if countdown > 0:
                return f"Countdown: {countdown} Sekunden"
            return "Zeit abgelaufen!"
        return "Fahrzeug bewegt sich."

    def reset_if_moved(self, tracking_id, position):
        """ Wenn sich ein geparktes Fahrzeug bewegt, entferne es aus parked_ids. """
        if tracking_id in self.parked_ids:
            distance = np.linalg.norm(self.last_position[tracking_id] - np.array(position))
            if distance > self.position_tolerance:
                self.parked_ids.remove(tracking_id)  # Fahrzeug bewegt sich -> zurücksetzen
                self.last_position[tracking_id] = position
                self.last_time[tracking_id] = time.time()
