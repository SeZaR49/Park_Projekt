import ffmpeg
import subprocess

def stream_init():
    """
    Startet den Kamera-Stream mit `libcamera-vid`, nutzt `ffmpeg`, um einzelne Frames zu extrahieren,
    und gibt den `ffmpeg`-Prozess sowie die Breite und Höhe des Streams zurück.
    """

    # Kamera-Stream-URL (UDP)
    stream_url = "udp://127.0.0.1:8554"

    # Starte libcamera-vid für den Stream
    subprocess.Popen(
        [
            "libcamera-vid",
            "-t", "0",  # Unbegrenzt streamen
            "--width", "1280",
            "--height", "720",
            "--framerate", "30",
            "--codec", "mjpeg",
            "-o", stream_url
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    # Standardauflösung
    width, height = 1280, 720

    print(f"🎥 Kamera-Stream gestartet mit {width}x{height}")

    # Starte `ffmpeg` mit kontinuierlicher Bildverarbeitung
    process = (
        ffmpeg
        .input(stream_url, format="mjpeg", fflags="nobuffer", r=30)  # Kontinuierliche Frames
        .output('pipe:', format='rawvideo', pix_fmt='rgb24', vsync="vfr")  # `vsync` verhindert Frame-Stopp
        .run_async(pipe_stdout=True, pipe_stderr=subprocess.DEVNULL)  # `stderr` versteckt Fehler
    )

    return process, width, height
