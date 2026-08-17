import cv2
import math
import time
import ctypes
from pathlib import Path

import mediapipe as mp
from pycaw.pycaw import AudioUtilities



# ============================================================
# MediaPipe Hand Landmarker
# ============================================================

BaseOptions = mp.tasks.BaseOptions
RunningMode = mp.tasks.vision.RunningMode
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

MODEL_PATH = "hand_landmarker.task"


# ============================================================
# Windows Media Keys
# ============================================================

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_STOP = 0xB2
VK_MEDIA_NEXT_TRACK = 0xB0
VK_VOLUME_MUTE = 0xAD


def press_key(key):
    """Send a Windows media-key press."""
    ctypes.windll.user32.keybd_event(key, 0, 0, 0)
    ctypes.windll.user32.keybd_event(key, 0, 2, 0)


# ============================================================
# Windows Volume Control
# ============================================================

devices = AudioUtilities.GetSpeakers()

volume = devices.EndpointVolume


def volume_up():
    """Increase system volume by 5%."""
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = min(current + 0.05, 1.0)
    volume.SetMasterVolumeLevelScalar(new_volume, None)


def volume_down():
    """Decrease system volume by 5%."""
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = max(current - 0.05, 0.0)
    volume.SetMasterVolumeLevelScalar(new_volume, None)


# ============================================================
# Distance between landmarks
# ============================================================

def distance(p1, p2):
    return math.hypot(
        p1.x - p2.x,
        p1.y - p2.y
    )


# ============================================================
# Gesture Recognition
# ============================================================

def recognize_gesture(landmarks):

    fingers = []

    # --------------------------------------------------------
    # Thumb
    # --------------------------------------------------------

    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    wrist = landmarks[0]

    if distance(thumb_tip, wrist) > distance(thumb_ip, wrist) * 1.1:
        fingers.append(1)
    else:
        fingers.append(0)

    # --------------------------------------------------------
    # Index, Middle, Ring, Pinky
    # --------------------------------------------------------

    finger_pairs = [
        (8, 6),    # Index
        (12, 10),  # Middle
        (16, 14),  # Ring
        (20, 18),  # Pinky
    ]

    for tip, pip in finger_pairs:

        if landmarks[tip].y < landmarks[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    total = sum(fingers)

    # --------------------------------------------------------
    # Gestures
    # --------------------------------------------------------

    # Open Palm
    if total == 5:
        return "OPEN PALM"

    # Fist
    if total == 0:
        return "FIST"

    # Thumb only
    if fingers == [1, 0, 0, 0, 0]:

        if landmarks[4].y < landmarks[3].y:
            return "THUMBS UP"
        else:
            return "THUMBS DOWN"

    # Victory
    if fingers == [0, 1, 1, 0, 0]:
        return "VICTORY"

    # Pointing
    if fingers == [0, 1, 0, 0, 0]:
        return "POINTING"

    # Three fingers
    if fingers == [0, 1, 1, 1, 0]:
        return "THREE"

    # Four fingers
    if fingers == [0, 1, 1, 1, 1]:
        return "FOUR"

    return "UNKNOWN"


# ============================================================
# Hand Drawing
# ============================================================

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),

    (0, 5), (5, 6), (6, 7), (7, 8),

    (5, 9), (9, 10), (10, 11), (11, 12),

    (9, 13), (13, 14), (14, 15), (15, 16),

    (13, 17), (17, 18), (18, 19), (19, 20),

    (0, 17)
]


def draw_hand(frame, landmarks, gesture):

    height, width, _ = frame.shape

    points = []

    # Draw landmarks
    for landmark in landmarks:

        x = int(landmark.x * width)
        y = int(landmark.y * height)

        points.append((x, y))

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 255, 0),
            -1
        )

    # Draw connections
    for start, end in CONNECTIONS:

        cv2.line(
            frame,
            points[start],
            points[end],
            (255, 0, 0),
            2
        )

    # Gesture text
    wrist_x, wrist_y = points[0]

    text_y = max(40, wrist_y - 30)

    cv2.putText(
        frame,
        gesture,
        (wrist_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )


# ============================================================
# Main Program
# ============================================================

def main():

    # Check model
    if not Path(MODEL_PATH).exists():

        print("ERROR: hand_landmarker.task was not found.")

        print(
            "Place hand_landmarker.task "
            "beside hand_gesture.py"
        )

        return

    # MediaPipe options
    options = HandLandmarkerOptions(

        base_options=BaseOptions(
            model_asset_path=MODEL_PATH
        ),

        running_mode=RunningMode.VIDEO,

        num_hands=1,

        min_hand_detection_confidence=0.5,

        min_hand_presence_confidence=0.5,

        min_tracking_confidence=0.5
    )

    # Webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print("ERROR: Could not open webcam.")

        return

    timestamp_ms = 0

    # Prevent actions from happening continuously
    last_action = ""

    last_action_time = 0

    ACTION_COOLDOWN = 1.0


    try:

        with HandLandmarker.create_from_options(options) as landmarker:

            while True:

                success, frame = cap.read()

                if not success:

                    print("ERROR: Could not read webcam frame.")

                    break


                # Mirror webcam
                frame = cv2.flip(frame, 1)


                # Convert BGR → RGB
                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )


                # MediaPipe image
                mp_image = mp.Image(

                    image_format=mp.ImageFormat.SRGB,

                    data=rgb_frame
                )


                # Timestamp
                timestamp_ms += 33


                # Detect hand
                result = landmarker.detect_for_video(

                    mp_image,

                    timestamp_ms
                )


                gesture = "NO HAND"

                action_text = ""


                if result.hand_landmarks:

                    hand_landmarks = result.hand_landmarks[0]

                    gesture = recognize_gesture(
                        hand_landmarks
                    )


                    current_time = time.time()


                    # ------------------------------------------------
                    # Perform action only after cooldown
                    # ------------------------------------------------

                    if current_time - last_action_time > ACTION_COOLDOWN:

                        # 👍 Volume Up
                        if gesture == "THUMBS UP":

                            volume_up()

                            action_text = "VOLUME UP"

                            last_action = action_text

                            last_action_time = current_time


                        # 👎 Volume Down
                        elif gesture == "THUMBS DOWN":

                            volume_down()

                            action_text = "VOLUME DOWN"

                            last_action = action_text

                            last_action_time = current_time


                        # ✋ Play / Pause
                        elif gesture == "OPEN PALM":

                            press_key(
                                VK_MEDIA_PLAY_PAUSE
                            )

                            action_text = "PLAY / PAUSE"

                            last_action = action_text

                            last_action_time = current_time


                        # ✊ Stop
                        elif gesture == "FIST":

                            press_key(
                                VK_MEDIA_STOP
                            )

                            action_text = "STOP"

                            last_action = action_text

                            last_action_time = current_time


                        # ✌️ Mute
                        elif gesture == "VICTORY":

                            press_key(
                                VK_VOLUME_MUTE
                            )

                            action_text = "MUTE"

                            last_action = action_text

                            last_action_time = current_time


                        # ☝️ Next Track
                        elif gesture == "POINTING":

                            press_key(
                                VK_MEDIA_NEXT_TRACK
                            )

                            action_text = "NEXT TRACK"

                            last_action = action_text

                            last_action_time = current_time


                    # Draw hand
                    draw_hand(
                        frame,
                        hand_landmarks,
                        gesture
                    )


                # ----------------------------------------------------
                # UI
                # ----------------------------------------------------

                cv2.putText(

                    frame,

                    "HAND GESTURE MEDIA CONTROLLER",

                    (20, 40),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.75,

                    (255, 255, 255),

                    2
                )


                # Current gesture
                cv2.putText(

                    frame,

                    f"Gesture: {gesture}",

                    (20, 75),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.65,

                    (0, 255, 255),

                    2
                )


                # Last action
                if last_action:

                    cv2.putText(

                        frame,

                        f"Action: {last_action}",

                        (20, 110),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.65,

                        (0, 255, 0),

                        2
                    )


                # Instructions
                cv2.putText(

                    frame,

                    "Q = Exit",

                    (20, 145),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    (255, 255, 255),

                    2
                )


                # Show webcam
                cv2.imshow(

                    "Hand Gesture Media Controller",

                    frame
                )


                # Exit
                if cv2.waitKey(1) & 0xFF == ord("q"):

                    break


    finally:

        cap.release()

        cv2.destroyAllWindows()


# ============================================================
# Program Entry
# ============================================================

if __name__ == "__main__":

    main()