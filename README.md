# Hand Tracking Mouse Control

Control your mouse with hand gestures using a webcam, MediaPipe Hand Landmarker, OpenCV, and PyAutoGUI.

## Features

- Real-time hand landmark detection from webcam input
- Cursor movement using the **right hand index fingertip**
- **Left click**: thumb + index pinch
- **Double click**: thumb + middle pinch
- **Right click**: thumb + ring pinch
- Basic cursor smoothing to reduce jitter

## Tech Stack

- Python
- OpenCV (`cv2`)
- MediaPipe Tasks (`HandLandmarker`)
- PyAutoGUI

## Project Files

- `hand_tracking.py` - main script for detection, gesture logic, and mouse control
- `hand_landmarker.task` - MediaPipe hand landmarker model used by the script

## Requirements

- Python 3.9+ (recommended)
- Webcam
- Windows/macOS/Linux desktop environment (PyAutoGUI controls system mouse)

Install dependencies:

```bash
pip install opencv-python mediapipe pyautogui
```

## Run

From the project directory:

```bash
python hand_tracking.py
```

Press `q` in the camera window to quit.

## How It Works

1. Webcam frames are captured with OpenCV.
2. Frames are converted to RGB and passed to MediaPipe Hand Landmarker in `VIDEO` mode.
3. For the detected **Right** hand, fingertip landmarks are tracked.
4. Index fingertip position inside a central rectangle is mapped to screen coordinates.
5. Pinch distances with thumb trigger click events with a cooldown delay.

## Gesture Controls

- Move cursor: move right index finger inside the blue rectangle
- Left click: touch thumb + index finger
- Double click: touch thumb + middle finger
- Right click: touch thumb + ring finger

## Important Notes

- Screen mapping is currently hardcoded for a specific monitor size (e.g., `1366x768`) and may require adjustment in `hand_tracking.py`.
- Gesture thresholds and click delays are fixed constants; tune them for your camera distance and lighting.
- `pyautogui.FAILSAFE` is disabled in this script. If needed, re-enable failsafe behavior for safety.

## Troubleshooting

- If the camera does not open, verify no other app is using it.
- If cursor movement feels off, adjust coordinate mapping constants in the script.
- If gestures trigger too often or not enough, adjust pinch `threshold` and `delay` values.
