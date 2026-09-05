import os
import time
import urllib.request

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    SERIAL_BAUDRATE,
    SERIAL_TIMEOUT,
    EAR_THRESHOLD,
    CLOSED_FRAMES,
    NUM_FACES,
    MODEL_FILENAME,
    CMD_LED_ON,
    CMD_LED_OFF,
    CMD_BUZZER,
)

from detection.ear import calculate_average_ear
from communication.esp32_serial import find_esp32_port, ESP32Serial


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/"
    "face_landmarker.task"
)


def download_model():
    """
    Download MediaPipe face landmark model if it does not exist.
    """

    if os.path.exists(MODEL_FILENAME):
        return

    print("[INFO] MediaPipe model not found.")
    print("[INFO] Downloading model...")

    urllib.request.urlretrieve(
        MODEL_URL,
        MODEL_FILENAME
    )

    print("[INFO] Model downloaded successfully.")


def draw_eye(frame, landmarks, indices):
    """
    Draw an eye contour on the frame.
    """

    points = []

    for index in indices:
        x = int(landmarks[index].x * frame.shape[1])
        y = int(landmarks[index].y * frame.shape[0])

        points.append((x, y))

    points = cv2.UMat(
        __import__("numpy").array(points, dtype="int32")
    )

    cv2.polylines(
        frame,
        [points.get()],
        True,
        (0, 255, 0),
        1
    )


def main():

    print("==============================")
    print("       EYE ALERT SYSTEM")
    print("==============================")

    # ---------------------------------
    # ESP32 connection
    # ---------------------------------

    esp32_port = find_esp32_port()

    if esp32_port is None:
        print("[ERROR] ESP32 serial port not found.")
        return

    print(f"[INFO] ESP32 detected on: {esp32_port}")

    esp32 = ESP32Serial(
        esp32_port,
        SERIAL_BAUDRATE,
        SERIAL_TIMEOUT
    )

    if not esp32.connect():
        return

    time.sleep(2)

    # ---------------------------------
    # MediaPipe model
    # ---------------------------------

    download_model()

    base_options = python.BaseOptions(
        model_asset_path=MODEL_FILENAME
    )

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=NUM_FACES
    )

    detector = vision.FaceLandmarker.create_from_options(
        options
    )

    # ---------------------------------
    # Camera
    # ---------------------------------

    camera = cv2.VideoCapture(CAMERA_INDEX)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    if not camera.isOpened():
        print("[ERROR] Could not open camera.")
        esp32.close()
        return

    print("[INFO] Camera started.")
    print("[INFO] Press Q to exit.")

    # ---------------------------------
    # Detection state
    # ---------------------------------

    closed_counter = 0
    buzzer_triggered = False

    previous_time = time.time()

    try:

        while True:

            success, frame = camera.read()

            if not success:
                print("[WARNING] Failed to read camera frame.")
                continue

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            detection_result = detector.detect(mp_image)

            # ---------------------------------
            # Face detected
            # ---------------------------------

            if detection_result.face_landmarks:

                landmarks = detection_result.face_landmarks[0]

                left_ear, right_ear, average_ear = (
                    calculate_average_ear(landmarks)
                )

                # ---------------------------------
                # Eyes closed
                # ---------------------------------

                if average_ear < EAR_THRESHOLD:

                    closed_counter += 1

                    cv2.putText(
                        frame,
                        "EYES CLOSED",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2
                    )

                    esp32.send_command(CMD_LED_ON)

                    # Trigger buzzer only once
                    if (
                        closed_counter >= CLOSED_FRAMES
                        and not buzzer_triggered
                    ):

                        esp32.send_command(CMD_BUZZER)

                        buzzer_triggered = True

                # ---------------------------------
                # Eyes open
                # ---------------------------------

                else:

                    closed_counter = 0
                    buzzer_triggered = False

                    cv2.putText(
                        frame,
                        "EYES OPEN",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

                    esp32.send_command(CMD_LED_OFF)

                # ---------------------------------
                # Display EAR
                # ---------------------------------

                cv2.putText(
                    frame,
                    f"EAR: {average_ear:.3f}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Closed frames: {closed_counter}",
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

            # ---------------------------------
            # No face
            # ---------------------------------

            else:

                closed_counter = 0
                buzzer_triggered = False

                esp32.send_command(CMD_LED_OFF)

                cv2.putText(
                    frame,
                    "NO FACE DETECTED",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )

            # ---------------------------------
            # FPS
            # ---------------------------------

            current_time = time.time()

            fps = 1.0 / max(
                current_time - previous_time,
                1e-6
            )

            previous_time = current_time

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 145),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "EYE ALERT",
                frame
            )

            # Q = quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        print("[INFO] Shutting down...")

        esp32.send_command(CMD_LED_OFF)

        camera.release()
        cv2.destroyAllWindows()
        esp32.close()

        print("[INFO] EYE ALERT stopped.")


if __name__ == "__main__":
    main()