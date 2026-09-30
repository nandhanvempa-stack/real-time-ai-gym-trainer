# Real-Time AI Gym Trainer

A real-time computer-vision fitness trainer that uses a webcam to estimate body pose, calculate joint angles, count exercise repetitions, and provide basic form feedback.

## Features

- Real-time webcam pose tracking
- Bicep curl repetition counting
- Squat repetition counting
- Push-up repetition counting
- UP/DOWN stage detection
- Joint-angle calculation using NumPy
- Basic form feedback
- On-screen exercise, reps, stage, and angle information

## Technologies

- Python
- OpenCV
- MediaPipe
- NumPy
- Git

## Setup

Use Python 3.10 or 3.11 for easiest MediaPipe compatibility.

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

## Controls

- `1` - Bicep curl
- `2` - Squat
- `3` - Push-up
- `R` - Reset repetitions
- `Q` - Quit

## How it works

The webcam frame is passed to MediaPipe Pose. Pose landmarks such as shoulders, elbows, wrists, hips, knees and ankles are detected. NumPy is then used to calculate the angle between three relevant landmarks.

For example, a bicep curl uses:

`Shoulder -> Elbow -> Wrist`

When the elbow angle moves below the contraction threshold and returns to the extended threshold, a repetition is counted.

The thresholds are deliberately simple so that the project remains understandable and easy to explain in an interview. They can be calibrated for different users and camera positions.

## Resume description

**Real-Time AI Gym Trainer | Python, OpenCV, MediaPipe, NumPy, Git**
- Built a real-time computer-vision fitness trainer that uses webcam-based pose estimation to track body movements during squats, push-ups and bicep curls.
- Calculated joint angles from detected body landmarks with NumPy to identify exercise stages and automatically count repetitions.
- Implemented threshold-based form feedback and an on-screen dashboard displaying exercise, repetition count, stage and joint angle.
