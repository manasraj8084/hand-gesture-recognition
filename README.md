# Hand Gesture Recognition

A real-time hand gesture recognition project built with **Python 3.13, OpenCV, and MediaPipe Hand Landmarker**.

The webcam captures live video, MediaPipe detects 21 hand landmarks, and the program analyzes finger positions to recognize common gestures.

## Features

- Real-time webcam recognition
- Supports up to two hands
- 21-point hand landmark visualization
- Open Palm
- Fist
- Thumbs Up
- Thumbs Down
- Victory / Peace
- Pointing
- Three fingers
- Four fingers
- Unknown gesture handling

## Tech Stack

- Python 3.13
- OpenCV
- MediaPipe Tasks API

## Project Structure

```text
hand-gesture-recognition/
├── hand_gesture.py
├── hand_landmarker.task        # downloaded separately
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
    └── demo.png                # optional
```

## 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/hand-gesture-recognition.git
cd hand-gesture-recognition
```

## 2. Install dependencies

Recommended: create a virtual environment first.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Then:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Download the MediaPipe model

Download the official Google MediaPipe Hand Landmarker model:

https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

Save the downloaded file as:

```text
hand_landmarker.task
```

Place it in the project root, beside `hand_gesture.py`.

> The model is required at runtime. Check the applicable MediaPipe/model license before redistributing the model file in your repository.

## 4. Run the project

```bash
python hand_gesture.py
```

Allow camera access if Windows asks for permission.

Press **Q** to close the application.

## How It Works

```text
Webcam
   ↓
OpenCV frame capture
   ↓
BGR → RGB conversion
   ↓
MediaPipe Hand Landmarker
   ↓
21 hand landmarks
   ↓
Finger-position analysis
   ↓
Gesture classification
   ↓
Gesture displayed on webcam
```

## Landmark Concept

MediaPipe provides 21 hand landmarks:

- `0` - Wrist
- `1–4` - Thumb
- `5–8` - Index finger
- `9–12` - Middle finger
- `13–16` - Ring finger
- `17–20` - Pinky

The program uses these landmark positions to determine which fingers are extended.

## Important Note

This is a rule-based gesture recognizer built on top of MediaPipe's hand landmark detection. It is not a separately trained neural network for gesture classes.

Accuracy can vary with:

- Hand orientation
- Lighting
- Camera angle
- Occlusion
- Distance from camera
- Different hand poses

## Future Improvements

- Add more gestures
- Add left/right hand-specific logic
- Improve thumb orientation detection
- Add gesture smoothing to reduce flickering
- Add gesture-controlled mouse
- Add volume control
- Add media controls
- Add screenshot capture
- Create a graphical user interface
- Add a custom machine-learning classifier

## License

This repository contains original project code. Third-party libraries and the MediaPipe model are subject to their respective licenses and terms.

## Author

**Your Name**

GitHub: https://github.com/YOUR-USERNAME
